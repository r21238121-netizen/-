from typing import Optional, Any, Union
from datetime import datetime
import json
import pickle
from redis.asyncio import Redis

from src.domain.entities import User, GameSession


class Cache:
    """Класс для работы с Redis кэшем"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def set_user(self, user: User, ttl: int = 3600) -> bool:
        """Сохранить пользователя в кэш"""
        try:
            user_data = {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'level': user.level,
                'chips': user.chips,
                'stars': user.stars,
                'experience': user.experience,
                'wins': user.wins,
                'losses': user.losses,
                'draws': user.draws,
                'referrals_count': user.referrals_count,
                'total_bets': user.total_bets,
                'role': user.role.value,
                'is_banned': user.is_banned,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat(),
                'last_daily_bonus': user.last_daily_bonus.isoformat() if user.last_daily_bonus else None,
                'referrer_id': user.referrer_id,
                'clan_id': user.clan_id
            }
            key = f"user:{user.telegram_id}"
            await self.redis.setex(key, ttl, json.dumps(user_data))
            return True
        except Exception:
            return False
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Получить пользователя из кэша"""
        try:
            key = f"user:{telegram_id}"
            user_data = await self.redis.get(key)
            if user_data:
                data = json.loads(user_data)
                return User(
                    id=data['id'],
                    telegram_id=data['telegram_id'],
                    username=data['username'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    level=data['level'],
                    chips=data['chips'],
                    stars=data['stars'],
                    experience=data['experience'],
                    wins=data['wins'],
                    losses=data['losses'],
                    draws=data['draws'],
                    referrals_count=data['referrals_count'],
                    total_bets=data['total_bets'],
                    role=__import__('src.domain.entities', fromlist=['UserRole']).UserRole(data['role']),
                    is_banned=data['is_banned'],
                    is_active=data['is_active'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    last_daily_bonus=datetime.fromisoformat(data['last_daily_bonus']) if data['last_daily_bonus'] else None,
                    referrer_id=data['referrer_id'],
                    clan_id=data['clan_id']
                )
            return None
        except Exception:
            return None
    
    async def delete_user(self, telegram_id: int) -> bool:
        """Удалить пользователя из кэша"""
        try:
            key = f"user:{telegram_id}"
            result = await self.redis.delete(key)
            return result > 0
        except Exception:
            return False
    
    async def set_game_session(self, session: GameSession, ttl: int = 7200) -> bool:
        """Сохранить игровую сессию в кэш"""
        try:
            session_data = {
                'id': session.id,
                'game_type': session.game_type.value,
                'status': session.status.value,
                'players': session.players,
                'bet_amount': session.bet_amount,
                'chat_id': session.chat_id,
                'created_at': session.created_at.isoformat(),
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'finished_at': session.finished_at.isoformat() if session.finished_at else None,
                'winner_id': session.winner_id,
                'metadata': session.metadata
            }
            key = f"game_session:{session.id}"
            await self.redis.setex(key, ttl, json.dumps(session_data))
            return True
        except Exception:
            return False
    
    async def get_game_session(self, session_id: str) -> Optional[GameSession]:
        """Получить игровую сессию из кэша"""
        try:
            key = f"game_session:{session_id}"
            session_data = await self.redis.get(key)
            if session_data:
                data = json.loads(session_data)
                return GameSession(
                    id=data['id'],
                    game_type=__import__('src.domain.entities', fromlist=['GameType']).GameType(data['game_type']),
                    status=__import__('src.domain.entities', fromlist=['GameStatus']).GameStatus(data['status']),
                    players=data['players'],
                    bet_amount=data['bet_amount'],
                    chat_id=data['chat_id'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    started_at=datetime.fromisoformat(data['started_at']) if data['started_at'] else None,
                    finished_at=datetime.fromisoformat(data['finished_at']) if data['finished_at'] else None,
                    winner_id=data['winner_id'],
                    metadata=data['metadata']
                )
            return None
        except Exception:
            return None
    
    async def delete_game_session(self, session_id: str) -> bool:
        """Удалить игровую сессию из кэша"""
        try:
            key = f"game_session:{session_id}"
            result = await self.redis.delete(key)
            return result > 0
        except Exception:
            return False
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Сохранить произвольное значение в кэш"""
        try:
            serialized_value = pickle.dumps(value)
            await self.redis.setex(key, ttl, serialized_value)
            return True
        except Exception:
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить произвольное значение из кэша"""
        try:
            value = await self.redis.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception:
            return None
    
    async def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа в кэше"""
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception:
            return False