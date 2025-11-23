from typing import Optional, List
from datetime import datetime
import uuid

from src.domain.entities import (
    User, GameSession, GameResult, GameType, GameStatus, 
    UserRole
)
from src.domain.repositories import (
    GameRepository, UserRepository, SessionRepository
)
from src.infrastructure.cache import Cache
from src.core.events import EventFactory, event_bus
from src.core.config import settings


class GameService:
    """Сервис для работы с играми"""
    
    def __init__(
        self, 
        game_repository: GameRepository,
        user_repository: UserRepository,
        session_repository: SessionRepository,
        cache: Cache
    ):
        self.game_repository = game_repository
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.cache = cache
    
    async def create_session(
        self, 
        game_type: GameType, 
        player1_id: str, 
        player2_id: str, 
        bet_amount: int, 
        chat_id: str
    ) -> Optional[GameSession]:
        """Создать игровую сессию"""
        # Проверяем, могут ли игроки сделать ставку
        player1 = await self.user_repository.get_by_id(player1_id)
        player2 = await self.user_repository.get_by_id(player2_id)
        
        if not player1 or not player2:
            return None
        
        if player1.chips < bet_amount or player2.chips < bet_amount:
            return None
        
        # Проверяем ограничения ставки
        if bet_amount < settings.game.min_bet or bet_amount > settings.game.max_bet:
            return None
        
        # Создаем сессию
        session = GameSession(
            id=f"session_{uuid.uuid4()}",
            game_type=game_type,
            status=GameStatus.WAITING,
            players=[player1_id, player2_id],
            bet_amount=bet_amount,
            chat_id=chat_id
        )
        
        created_session = await self.session_repository.create(session)
        
        # Списываем ставки у игроков
        await self.user_repository.update(player1_id, chips=player1.chips - bet_amount)
        await self.user_repository.update(player2_id, chips=player2.chips - bet_amount)
        
        # Обновляем кэш
        player1.chips -= bet_amount
        player2.chips -= bet_amount
        await self.cache.set_user(player1)
        await self.cache.set_user(player2)
        
        return created_session
    
    async def start_game(self, session_id: str) -> Optional[GameSession]:
        """Начать игру"""
        session = await self.session_repository.get_by_id(session_id)
        if not session or session.status != GameStatus.WAITING:
            return None
        
        # Обновляем статус игры
        updated_session = await self.session_repository.update(
            session_id, 
            status=GameStatus.ACTIVE,
            started_at=datetime.utcnow()
        )
        
        if updated_session:
            # Сохраняем в кэш
            await self.cache.set_game_session(updated_session)
        
        return updated_session
    
    async def finish_game(
        self, 
        session_id: str, 
        winner_id: str,
        loser_id: str
    ) -> Optional[GameResult]:
        """Завершить игру и распределить награды"""
        session = await self.session_repository.get_by_id(session_id)
        if not session or session.status != GameStatus.ACTIVE:
            return None
        
        # Обновляем статус сессии
        updated_session = await self.session_repository.update(
            session_id,
            status=GameStatus.FINISHED,
            winner_id=winner_id,
            finished_at=datetime.utcnow()
        )
        
        if not updated_session:
            return None
        
        # Рассчитываем награды
        total_pot = session.bet_amount * 2  # Обе ставки в банке
        winner_reward = total_pot  # Победитель забирает всё
        
        # Обновляем балансы
        winner = await self.user_repository.get_by_id(winner_id)
        loser = await self.user_repository.get_by_id(loser_id)
        
        if not winner or not loser:
            return None
        
        # Начисляем выигрыш победителю
        new_winner_chips = winner.chips + winner_reward
        await self.user_repository.update(winner_id, chips=new_winner_chips, wins=winner.wins + 1)
        
        # Увеличиваем количество проигрышей у проигравшего
        await self.user_repository.update(loser_id, losses=loser.losses + 1)
        
        # Обновляем статистику в кэше
        winner.chips = new_winner_chips
        winner.wins += 1
        loser.losses += 1
        await self.cache.set_user(winner)
        await self.cache.set_user(loser)
        
        # Создаем результат игры
        result = GameResult(
            game_id=session_id,
            winner_id=winner_id,
            loser_id=loser_id,
            game_type=session.game_type,
            bet_amount=session.bet_amount
        )
        
        # Сохраняем результат
        saved_result = await self.game_repository.save_result(result)
        
        # Публикуем событие завершения игры
        event = EventFactory.game_finished(
            session_id,
            winner_id,
            loser_id,
            session.game_type.value,
            session.bet_amount
        )
        await event_bus.publish(event)
        
        # Добавляем опыт победителю
        await self.user_repository.update(
            winner_id, 
            experience=winner.experience + session.bet_amount // 10
        )
        
        return saved_result
    
    async def get_active_sessions(self, chat_id: str) -> List[GameSession]:
        """Получить активные сессии в чате"""
        return await self.game_repository.get_active_games(chat_id)
    
    async def get_user_session(self, user_id: str) -> Optional[GameSession]:
        """Получить активную сессию пользователя"""
        return await self.session_repository.get_user_session(user_id)
    
    async def cancel_session(self, session_id: str) -> bool:
        """Отменить сессию (возврат ставок)"""
        session = await self.session_repository.get_by_id(session_id)
        if not session or session.status != GameStatus.WAITING:
            return False
        
        # Возвращаем ставки игрокам
        for player_id in session.players:
            player = await self.user_repository.get_by_id(player_id)
            if player:
                new_chips = player.chips + session.bet_amount
                await self.user_repository.update(player_id, chips=new_chips)
                
                # Обновляем кэш
                player.chips = new_chips
                await self.cache.set_user(player)
        
        # Обновляем статус сессии
        success = await self.session_repository.update(
            session_id,
            status=GameStatus.CANCELLED
        )
        
        return success is not None
    
    async def get_game_results(self, user_id: str, limit: int = 10) -> List[GameResult]:
        """Получить результаты игр пользователя"""
        return await self.game_repository.get_game_results(user_id, limit)
    
    async def get_user_stats(self, user_id: str) -> Optional[dict]:
        """Получить статистику пользователя по играм"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        results = await self.get_game_results(user_id, 100)  # последние 100 игр
        
        total_games = len(results)
        wins = sum(1 for r in results if r.winner_id == user_id)
        losses = total_games - wins
        
        total_bet = sum(r.bet_amount for r in results)
        total_won = sum(r.bet_amount * 2 for r in results if r.winner_id == user_id)
        
        return {
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "win_rate": wins / total_games * 100 if total_games > 0 else 0,
            "total_bet": total_bet,
            "total_won": total_won,
            "net_chips": total_won - total_bet
        }