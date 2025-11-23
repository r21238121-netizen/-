from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime


class EventType(Enum):
    """Типы доменных событий"""
    # Пользовательские события
    USER_REGISTERED = "user_registered"
    USER_LEVEL_UP = "user_level_up"
    USER_REFERRED = "user_referred"
    USER_BALANCE_CHANGED = "user_balance_changed"
    
    # Игровые события
    GAME_STARTED = "game_started"
    GAME_FINISHED = "game_finished"
    PLAYER_WON = "player_won"
    PLAYER_LOST = "player_lost"
    PLAYER_DRAW = "player_draw"
    
    # Сессионные события
    SESSION_CREATED = "session_created"
    SESSION_CLOSED = "session_closed"
    
    # Административные события
    ADMIN_ACTION = "admin_action"
    USER_BANNED = "user_banned"
    USER_UNBANNED = "user_unbanned"
    GAME_DISABLED = "game_disabled"
    GAME_ENABLED = "game_enabled"


@dataclass
class DomainEvent:
    """Базовое доменное событие"""
    type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    aggregate_id: Optional[str] = None
    aggregate_type: Optional[str] = None


class EventBus:
    """Шина доменных событий"""
    
    def __init__(self):
        self._handlers = {}
    
    def subscribe(self, event_type: EventType, handler):
        """Подписка на событие"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: DomainEvent):
        """Публикация события"""
        handlers = self._handlers.get(event.type, [])
        for handler in handlers:
            await handler(event)


# Глобальная шина событий
event_bus = EventBus()


# Фабрика событий
class EventFactory:
    """Фабрика для создания доменных событий"""
    
    @staticmethod
    def user_registered(user_id: str, chat_id: str) -> DomainEvent:
        return DomainEvent(
            type=EventType.USER_REGISTERED,
            timestamp=datetime.utcnow(),
            data={
                "user_id": user_id,
                "chat_id": chat_id
            },
            aggregate_id=user_id,
            aggregate_type="User"
        )
    
    @staticmethod
    def user_referred(referrer_id: str, referred_id: str) -> DomainEvent:
        return DomainEvent(
            type=EventType.USER_REFERRED,
            timestamp=datetime.utcnow(),
            data={
                "referrer_id": referrer_id,
                "referred_id": referred_id
            },
            aggregate_id=referrer_id,
            aggregate_type="User"
        )
    
    @staticmethod
    def game_finished(
        game_id: str,
        winner_id: str,
        loser_id: str,
        game_type: str,
        bet_amount: int
    ) -> DomainEvent:
        return DomainEvent(
            type=EventType.GAME_FINISHED,
            timestamp=datetime.utcnow(),
            data={
                "game_id": game_id,
                "winner_id": winner_id,
                "loser_id": loser_id,
                "game_type": game_type,
                "bet_amount": bet_amount
            },
            aggregate_id=game_id,
            aggregate_type="Game"
        )
    
    @staticmethod
    def user_balance_changed(
        user_id: str,
        old_balance: int,
        new_balance: int,
        reason: str
    ) -> DomainEvent:
        return DomainEvent(
            type=EventType.USER_BALANCE_CHANGED,
            timestamp=datetime.utcnow(),
            data={
                "user_id": user_id,
                "old_balance": old_balance,
                "new_balance": new_balance,
                "reason": reason
            },
            aggregate_id=user_id,
            aggregate_type="User"
        )