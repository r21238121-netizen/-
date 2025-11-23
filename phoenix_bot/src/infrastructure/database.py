from typing import Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from src.core.config import settings


Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    level = Column(Integer, default=1)
    chips = Column(Integer, default=0)
    stars = Column(Integer, default=0)
    experience = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    referrals_count = Column(Integer, default=0)
    total_bets = Column(Integer, default=0)
    role = Column(String, default="player")  # player, moderator, admin, owner
    is_banned = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_daily_bonus = Column(DateTime, nullable=True)
    referrer_id = Column(String, nullable=True)
    clan_id = Column(String, nullable=True)


class GameSessionDB(Base):
    __tablename__ = "game_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    game_type = Column(String, nullable=False)  # blackjack, dice, rps, etc.
    status = Column(String, default="waiting")  # waiting, active, finished, cancelled
    players = Column(JSON, nullable=False)  # JSON array of user IDs
    bet_amount = Column(Integer, nullable=False)
    chat_id = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    winner_id = Column(String, nullable=True)
    game_metadata = Column(JSON, nullable=True)  # Additional game-specific data


class ClanDB(Base):
    __tablename__ = "clans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    owner_id = Column(String, nullable=False)
    members = Column(JSON, default=list)  # JSON array of user IDs
    level = Column(Integer, default=1)
    reputation = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class GameResultDB(Base):
    __tablename__ = "game_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String, nullable=False)
    winner_id = Column(String, nullable=False)
    loser_id = Column(String, nullable=False)
    game_type = Column(String, nullable=False)
    bet_amount = Column(Integer, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    metadata = Column(JSON, nullable=True)


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, database_url: str, pool_size: int = 20, pool_overflow: int = 10):
        self.database_url = database_url
        self.pool_size = pool_size
        self.pool_overflow = pool_overflow
        self.engine = None
        self.async_session = None
    
    async def init_db(self):
        """Инициализация базы данных"""
        self.engine = create_async_engine(
            self.database_url,
            pool_size=self.pool_size,
            max_overflow=self.pool_overflow,
            echo=False  # В продакшене отключить
        )
        
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Создание таблиц
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Закрытие соединения с базой данных"""
        if self.engine:
            await self.engine.dispose()