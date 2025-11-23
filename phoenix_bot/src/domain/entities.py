from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """Роли пользователей в системе"""
    PLAYER = "player"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"


class GameType(Enum):
    """Типы игр"""
    BLACKJACK = "blackjack"
    DICE = "dice"
    RPS = "rps"
    WORD_DUEL = "word_duel"
    SLOT_MACHINE = "slot_machine"
    QUEST = "quest"
    BOSS_RUSH = "boss_rush"


class GameStatus(Enum):
    """Статусы игровых сессий"""
    WAITING = "waiting"
    ACTIVE = "active"
    FINISHED = "finished"
    CANCELLED = "cancelled"


@dataclass
class User:
    """Сущность пользователя"""
    id: str
    telegram_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    level: int = 1
    chips: int = 0
    stars: int = 0
    experience: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    referrals_count: int = 0
    total_bets: int = 0
    role: UserRole = UserRole.PLAYER
    is_banned: bool = False
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    last_daily_bonus: Optional[datetime] = None
    referrer_id: Optional[str] = None
    clan_id: Optional[str] = None
    
    def add_chips(self, amount: int, reason: str = "unknown") -> int:
        """Добавить фишки пользователю"""
        self.chips += amount
        self.updated_at = datetime.utcnow()
        return self.chips
    
    def remove_chips(self, amount: int) -> bool:
        """Списать фишки у пользователя"""
        if self.chips >= amount:
            self.chips -= amount
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def add_experience(self, amount: int) -> int:
        """Добавить опыт пользователю"""
        self.experience += amount
        self.updated_at = datetime.utcnow()
        return self.experience
    
    def get_next_level_exp(self) -> int:
        """Получить количество опыта для следующего уровня"""
        return self.level * 100
    
    def level_up(self) -> bool:
        """Повысить уровень пользователя"""
        if self.experience >= self.get_next_level_exp():
            self.level += 1
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_rank(self) -> str:
        """Получить ранг пользователя по уровню"""
        ranks = [
            "Новичок", "Бронза", "Серебро", "Золото", 
            "Платина", "Алмаз", "Легенда"
        ]
        rank_index = min(self.level // 5, len(ranks) - 1)
        return ranks[rank_index]


@dataclass
class GameSession:
    """Сущность игровой сессии"""
    id: str
    game_type: GameType
    status: GameStatus
    players: List[str]  # список user_id
    bet_amount: int
    chat_id: str
    created_at: datetime = datetime.utcnow()
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    winner_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def add_player(self, user_id: str) -> bool:
        """Добавить игрока в сессию"""
        if len(self.players) < 2 and user_id not in self.players:
            self.players.append(user_id)
            return True
        return False
    
    def start_game(self):
        """Начать игру"""
        self.status = GameStatus.ACTIVE
        self.started_at = datetime.utcnow()
    
    def finish_game(self, winner_id: str):
        """Завершить игру"""
        self.status = GameStatus.FINISHED
        self.winner_id = winner_id
        self.finished_at = datetime.utcnow()


@dataclass
class Clan:
    """Сущность клана"""
    id: str
    name: str
    owner_id: str
    members: List[str]  # список user_id
    level: int = 1
    reputation: int = 0
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    def add_member(self, user_id: str) -> bool:
        """Добавить участника в клан"""
        if len(self.members) < 10 and user_id not in self.members:
            self.members.append(user_id)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def remove_member(self, user_id: str) -> bool:
        """Удалить участника из клана"""
        if user_id in self.members and user_id != self.owner_id:
            self.members.remove(user_id)
            self.updated_at = datetime.utcnow()
            return True
        return False


@dataclass
class Achievement:
    """Сущность достижения"""
    id: str
    name: str
    description: str
    icon: str
    exp_reward: int
    chip_reward: int
    requirement: Dict[str, Any]  # условия получения
    created_at: datetime = datetime.utcnow()


@dataclass
class GameResult:
    """Результат игры"""
    game_id: str
    winner_id: str
    loser_id: str
    game_type: GameType
    bet_amount: int
    timestamp: datetime = datetime.utcnow()
    metadata: Dict[str, Any] = None