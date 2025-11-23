from typing import Optional, List
from datetime import datetime

from src.domain.entities import User, GameSession, GameType, UserRole
from src.domain.repositories import UserRepository, GameRepository, SessionRepository
from src.core.events import EventFactory, event_bus


class AdminService:
    """Сервис для административных операций"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        game_repository: GameRepository,
        session_repository: SessionRepository
    ):
        self.user_repository = user_repository
        self.game_repository = game_repository
        self.session_repository = session_repository
    
    async def set_user_balance(self, admin_id: str, user_id: str, new_balance: int) -> Optional[User]:
        """Установить баланс пользователю (только админ)"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        old_balance = user.chips
        updated_user = await self.user_repository.update(user_id, chips=new_balance)
        
        if updated_user:
            # Публикуем административное событие
            event = EventFactory.user_balance_changed(
                user_id,
                old_balance,
                new_balance,
                f"admin_action_by_{admin_id}"
            )
            await event_bus.publish(event)
        
        return updated_user
    
    async def add_to_balance(self, admin_id: str, user_id: str, amount: int) -> Optional[User]:
        """Добавить к балансу пользователя (только админ)"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        new_balance = user.chips + amount
        updated_user = await self.user_repository.update(user_id, chips=new_balance)
        
        if updated_user:
            # Публикуем административное событие
            event = EventFactory.user_balance_changed(
                user_id,
                user.chips,
                new_balance,
                f"admin_action_by_{admin_id}"
            )
            await event_bus.publish(event)
        
        return updated_user
    
    async def ban_user(self, admin_id: str, user_id: str, reason: str = "unknown") -> Optional[User]:
        """Заблокировать пользователя"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        updated_user = await self.user_repository.update(user_id, is_banned=True)
        
        if updated_user:
            # Публикуем событие
            event = EventFactory(
                type="user_banned",
                timestamp=datetime.utcnow(),
                data={
                    "admin_id": admin_id,
                    "user_id": user_id,
                    "reason": reason
                },
                aggregate_id=user_id,
                aggregate_type="User"
            )
            await event_bus.publish(event)
        
        return updated_user
    
    async def unban_user(self, admin_id: str, user_id: str) -> Optional[User]:
        """Разблокировать пользователя"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        updated_user = await self.user_repository.update(user_id, is_banned=False)
        
        if updated_user:
            # Публикуем событие
            event = EventFactory(
                type="user_unbanned",
                timestamp=datetime.utcnow(),
                data={
                    "admin_id": admin_id,
                    "user_id": user_id
                },
                aggregate_id=user_id,
                aggregate_type="User"
            )
            await event_bus.publish(event)
        
        return updated_user
    
    async def set_user_role(self, admin_id: str, user_id: str, role: UserRole) -> Optional[User]:
        """Установить роль пользователю"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        updated_user = await self.user_repository.update(user_id, role=role.value)
        
        if updated_user:
            # Публикуем событие
            event = EventFactory(
                type="admin_action",
                timestamp=datetime.utcnow(),
                data={
                    "admin_id": admin_id,
                    "user_id": user_id,
                    "action": "set_role",
                    "role": role.value
                },
                aggregate_id=user_id,
                aggregate_type="User"
            )
            await event_bus.publish(event)
        
        return updated_user
    
    async def get_user_stats(self, user_id: str) -> Optional[dict]:
        """Получить полную статистику пользователя"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        # Получаем активные игры пользователя
        active_games = await self.session_repository.get_user_session(user_id)
        
        return {
            "user_info": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "level": user.level,
                "chips": user.chips,
                "stars": user.stars,
                "experience": user.experience,
                "role": user.role.value,
                "is_banned": user.is_banned,
                "created_at": user.created_at,
                "referrals_count": user.referrals_count
            },
            "game_stats": {
                "wins": user.wins,
                "losses": user.losses,
                "draws": user.draws,
                "total_bets": user.total_bets
            },
            "active_sessions": active_games.id if active_games else None
        }
    
    async def get_chat_stats(self, chat_id: str) -> dict:
        """Получить статистику чата"""
        # Получаем пользователей чата (в упрощенном виде - всех пользователей)
        # В реальном приложении потребуется отдельная таблица связи пользователь-чат
        top_users = await self.user_repository.get_top_users(10)
        
        # Получаем активные игры в чате
        active_games = await self.game_repository.get_active_games(chat_id)
        
        return {
            "chat_id": chat_id,
            "total_users": len(top_users),
            "active_games": len(active_games),
            "top_users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "chips": user.chips,
                    "level": user.level
                } for user in top_users
            ],
            "active_games_list": [
                {
                    "id": game.id,
                    "game_type": game.game_type.value,
                    "players": game.players,
                    "bet_amount": game.bet_amount,
                    "created_at": game.created_at
                } for game in active_games
            ]
        }
    
    async def disable_game(self, admin_id: str, game_type: GameType) -> bool:
        """Отключить игру (временно)"""
        # В реальном приложении это бы требовало хранения настроек игр
        # Пока просто публикуем событие
        event = EventFactory(
            type="game_disabled",
            timestamp=datetime.utcnow(),
            data={
                "admin_id": admin_id,
                "game_type": game_type.value
            },
            aggregate_type="Game"
        )
        await event_bus.publish(event)
        return True
    
    async def enable_game(self, admin_id: str, game_type: GameType) -> bool:
        """Включить игру"""
        # В реальном приложении это бы требовало хранения настроек игр
        # Пока просто публикуем событие
        event = EventFactory(
            type="game_enabled",
            timestamp=datetime.utcnow(),
            data={
                "admin_id": admin_id,
                "game_type": game_type.value
            },
            aggregate_type="Game"
        )
        await event_bus.publish(event)
        return True
    
    async def get_all_active_sessions(self) -> List[GameSession]:
        """Получить все активные сессии"""
        return await self.session_repository.get_active_sessions()
    
    async def force_end_session(self, admin_id: str, session_id: str) -> bool:
        """Принудительно завершить сессию"""
        session = await self.session_repository.get_by_id(session_id)
        if not session:
            return False
        
        # Обновляем статус сессии на cancelled
        updated_session = await self.session_repository.update(
            session_id,
            status="cancelled"
        )
        
        if updated_session:
            # Публикуем событие административного вмешательства
            event = EventFactory(
                type="admin_action",
                timestamp=datetime.utcnow(),
                data={
                    "admin_id": admin_id,
                    "session_id": session_id,
                    "action": "force_end_session"
                },
                aggregate_id=session_id,
                aggregate_type="GameSession"
            )
            await event_bus.publish(event)
        
        return updated_session is not None