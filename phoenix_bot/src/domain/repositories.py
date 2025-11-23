from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.domain.entities import User, GameSession, Clan, Achievement, GameResult


class UserRepository(ABC):
    """Абстрактный репозиторий пользователей"""
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def update(self, user_id: str, **kwargs) -> Optional[User]:
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_top_users(self, limit: int = 10) -> List[User]:
        pass
    
    @abstractmethod
    async def get_chat_top_users(self, chat_id: str, limit: int = 10) -> List[User]:
        pass
    
    @abstractmethod
    async def increment_referrals(self, user_id: str) -> Optional[User]:
        pass


class GameRepository(ABC):
    """Абстрактный репозиторий игр"""
    
    @abstractmethod
    async def get_by_id(self, game_id: str) -> Optional[GameSession]:
        pass
    
    @abstractmethod
    async def create(self, game_session: GameSession) -> GameSession:
        pass
    
    @abstractmethod
    async def update(self, game_id: str, **kwargs) -> Optional[GameSession]:
        pass
    
    @abstractmethod
    async def delete(self, game_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_active_games(self, chat_id: str) -> List[GameSession]:
        pass
    
    @abstractmethod
    async def get_user_active_games(self, user_id: str) -> List[GameSession]:
        pass
    
    @abstractmethod
    async def save_result(self, result: GameResult) -> GameResult:
        pass
    
    @abstractmethod
    async def get_game_results(self, user_id: str, limit: int = 10) -> List[GameResult]:
        pass


class SessionRepository(ABC):
    """Абстрактный репозиторий сессий"""
    
    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[GameSession]:
        pass
    
    @abstractmethod
    async def create(self, session: GameSession) -> GameSession:
        pass
    
    @abstractmethod
    async def update(self, session_id: str, **kwargs) -> Optional[GameSession]:
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_active_sessions(self) -> List[GameSession]:
        pass
    
    @abstractmethod
    async def get_user_session(self, user_id: str) -> Optional[GameSession]:
        pass


class ClanRepository(ABC):
    """Абстрактный репозиторий кланов"""
    
    @abstractmethod
    async def get_by_id(self, clan_id: str) -> Optional[Clan]:
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Clan]:
        pass
    
    @abstractmethod
    async def create(self, clan: Clan) -> Clan:
        pass
    
    @abstractmethod
    async def update(self, clan_id: str, **kwargs) -> Optional[Clan]:
        pass
    
    @abstractmethod
    async def delete(self, clan_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_user_clan(self, user_id: str) -> Optional[Clan]:
        pass
    
    @abstractmethod
    async def get_top_clans(self, limit: int = 10) -> List[Clan]:
        pass