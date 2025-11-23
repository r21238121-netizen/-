from typing import Protocol, Dict, Any, Optional
from dependency_injector import containers, providers
from dependency_injector.providers import Singleton, Factory
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from redis.asyncio import Redis

from src.core.config import settings
from src.infrastructure.database import Database
from src.infrastructure.cache import Cache
from src.application.game_service import GameService
from src.application.admin_service import AdminService
from src.application.user_service import UserService
from src.domain.repositories import (
    UserRepository,
    GameRepository,
    SessionRepository,
    ClanRepository
)
from src.infrastructure.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyGameRepository,
    SQLAlchemySessionRepository,
    SQLAlchemyClanRepository
)
from src.adapters.telegram_handler import TelegramHandler
from src.admin.admin_service import TelegramAdminService


class Container(containers.DeclarativeContainer):
    """DI контейнер для приложения"""
    
    # Конфигурация
    config = providers.Configuration()
    
    # База данных
    database = providers.Singleton(
        Database,
        database_url=settings.database_url,
        pool_size=settings.database_pool_size,
        pool_overflow=settings.database_pool_overflow
    )
    
    # Redis
    redis = providers.Singleton(
        Redis,
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password
    )
    
    # Кэш
    cache = providers.Singleton(
        Cache,
        redis_client=redis
    )
    
    # Репозитории
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session_factory=database.provided.async_session
    )
    
    game_repository = providers.Factory(
        SQLAlchemyGameRepository,
        session_factory=database.provided.async_session
    )
    
    session_repository = providers.Factory(
        SQLAlchemySessionRepository,
        session_factory=database.provided.async_session
    )
    
    clan_repository = providers.Factory(
        SQLAlchemyClanRepository,
        session_factory=database.provided.async_session
    )
    
    # Сервисы
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        cache=cache
    )
    
    game_service = providers.Factory(
        GameService,
        game_repository=game_repository,
        user_repository=user_repository,
        session_repository=session_repository,
        cache=cache
    )
    
    admin_service = providers.Factory(
        AdminService,
        user_repository=user_repository,
        game_repository=game_repository,
        session_repository=session_repository
    )
    
    # Админ сервис
    telegram_admin_service = providers.Factory(
        TelegramAdminService,
        admin_service=admin_service,
        user_service=user_service
    )
    
    # Адаптеры
    telegram_handler = providers.Factory(
        TelegramHandler,
        game_service=game_service,
        admin_service=telegram_admin_service,
        user_service=user_service,
        config=config
    )


# Глобальный контейнер
container = Container()
container.config.from_dict(settings.dict())