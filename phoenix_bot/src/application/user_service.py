from typing import Optional
from datetime import datetime, timedelta

from src.domain.entities import User, UserRole
from src.domain.repositories import UserRepository
from src.infrastructure.cache import Cache
from src.core.events import EventFactory, event_bus
from src.core.config import settings


class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, user_repository: UserRepository, cache: Cache):
        self.user_repository = user_repository
        self.cache = cache
    
    async def register_user(
        self, 
        telegram_id: int, 
        username: Optional[str], 
        first_name: str, 
        last_name: Optional[str] = None,
        referrer_id: Optional[str] = None
    ) -> Optional[User]:
        """Регистрация нового пользователя"""
        # Проверяем, существует ли пользователь
        existing_user = await self.user_repository.get_by_telegram_id(telegram_id)
        if existing_user:
            return existing_user
        
        # Создаем нового пользователя
        user = User(
            id=f"user_{telegram_id}",
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            chips=settings.game.initial_chips,
            stars=0,
            experience=0,
            referrer_id=referrer_id
        )
        
        created_user = await self.user_repository.create(user)
        
        # Публикуем событие
        event = EventFactory.user_registered(user.id, "global")
        await event_bus.publish(event)
        
        # Добавляем в кэш
        await self.cache.set_user(created_user)
        
        # Если есть реферер, увеличиваем ему счетчик
        if referrer_id:
            await self.process_referral(referrer_id, user.id)
        
        return created_user
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя по telegram_id"""
        # Сначала пытаемся получить из кэша
        user = await self.cache.get_user(telegram_id)
        if user:
            return user
        
        # Если в кэше нет, получаем из репозитория
        user = await self.user_repository.get_by_telegram_id(telegram_id)
        if user:
            # Сохраняем в кэш
            await self.cache.set_user(user)
        
        return user
    
    async def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Обновить данные пользователя"""
        updated_user = await self.user_repository.update(user_id, **kwargs)
        if updated_user:
            # Обновляем в кэше
            await self.cache.set_user(updated_user)
        return updated_user
    
    async def add_chips(self, user_id: str, amount: int, reason: str = "unknown") -> Optional[User]:
        """Добавить фишки пользователю"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        new_chips = user.chips + amount
        updated_user = await self.user_repository.update(user_id, chips=new_chips)
        if updated_user:
            # Обновляем в кэше
            await self.cache.set_user(updated_user)
            
            # Публикуем событие изменения баланса
            event = EventFactory.user_balance_changed(
                user_id, 
                user.chips, 
                new_chips, 
                reason
            )
            await event_bus.publish(event)
        
        return updated_user
    
    async def remove_chips(self, user_id: str, amount: int) -> bool:
        """Списать фишки у пользователя"""
        user = await self.user_repository.get_by_id(user_id)
        if not user or user.chips < amount:
            return False
        
        new_chips = user.chips - amount
        updated_user = await self.user_repository.update(user_id, chips=new_chips)
        if updated_user:
            # Обновляем в кэше
            await self.cache.set_user(updated_user)
            
            # Публикуем событие изменения баланса
            event = EventFactory.user_balance_changed(
                user_id, 
                user.chips, 
                new_chips, 
                "bet"
            )
            await event_bus.publish(event)
        
        return updated_user is not None
    
    async def add_experience(self, user_id: str, amount: int) -> Optional[User]:
        """Добавить опыт пользователю"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        new_experience = user.experience + amount
        updated_user = await self.user_repository.update(user_id, experience=new_experience)
        if updated_user:
            # Проверяем, повысился ли уровень
            old_level = user.level
            if updated_user.level_up():
                # Уровень повысился, обновляем в БД
                updated_user = await self.user_repository.update(
                    user_id, 
                    level=updated_user.level,
                    experience=updated_user.experience
                )
            
            # Обновляем в кэше
            await self.cache.set_user(updated_user)
        return updated_user
    
    async def process_referral(self, referrer_id: str, referred_id: str) -> bool:
        """Обработать рефералку"""
        # Начисляем бонус рефереру
        referrer = await self.add_chips(referrer_id, settings.game.referral_bonus, "referral")
        if not referrer:
            return False
        
        # Увеличиваем счетчик рефералов
        referrer = await self.user_repository.increment_referrals(referrer_id)
        if referrer:
            await self.cache.set_user(referrer)
        
        # Публикуем событие
        event = EventFactory.user_referred(referrer_id, referred_id)
        await event_bus.publish(event)
        
        return True
    
    async def get_top_users(self, limit: int = 10) -> list[User]:
        """Получить топ пользователей"""
        return await self.user_repository.get_top_users(limit)
    
    async def claim_daily_bonus(self, user_id: str) -> Optional[User]:
        """Получить ежедневный бонус"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        now = datetime.utcnow()
        # Проверяем, можно ли получить бонус (раз в 24 часа)
        if user.last_daily_bonus and (now - user.last_daily_bonus) < timedelta(days=1):
            return user  # Уже получал бонус за последние 24 часа
        
        # Рассчитываем бонус с учетом активных рефералов
        bonus_amount = settings.game.daily_bonus
        if user.referrals_count > 0:
            bonus_amount += user.referrals_count * 10  # 10 фишек за каждого активного реферала
            bonus_amount = min(bonus_amount, 
                              settings.game.daily_bonus * settings.game.max_daily_bonus_multiplier)
        
        # Добавляем бонус
        updated_user = await self.add_chips(user_id, bonus_amount, "daily_bonus")
        if updated_user:
            # Обновляем время получения бонуса
            updated_user = await self.user_repository.update(
                user_id, 
                last_daily_bonus=now
            )
            if updated_user:
                await self.cache.set_user(updated_user)
        
        return updated_user
    
    async def set_user_role(self, user_id: str, role: UserRole) -> Optional[User]:
        """Установить роль пользователю"""
        updated_user = await self.user_repository.update(user_id, role=role.value)
        if updated_user:
            await self.cache.set_user(updated_user)
        return updated_user