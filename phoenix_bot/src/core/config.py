from typing import Optional
from dataclasses import dataclass
from pydantic import BaseSettings


@dataclass
class GameConfig:
    """Конфигурация игровых механик"""
    # Начальные значения
    initial_chips: int = 500
    daily_bonus: int = 100
    referral_bonus: int = 200
    invite_bonus: int = 1500
    
    # Ограничения
    max_bet: int = 10000
    min_bet: int = 10
    max_daily_bonus_multiplier: int = 10  # за активных рефералов
    
    # Настройки игр
    blackjack_deck_count: int = 1
    dice_sides: int = 6
    word_duel_time_limit: int = 60  # секунд
    slot_cost: int = 50


class Settings(BaseSettings):
    """Основные настройки приложения"""
    # Telegram
    telegram_token: str
    telegram_api_id: Optional[str] = None
    telegram_api_hash: Optional[str] = None
    
    # База данных
    database_url: str = "sqlite+aiosqlite:///./phoenix_bot.db"
    database_pool_size: int = 20
    database_pool_overflow: int = 10
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Логирование
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Безопасность
    rate_limit_requests: int = 10  # за 10 секунд
    session_timeout: int = 3600  # секунд
    max_concurrent_sessions: int = 5
    
    # Игровая конфигурация
    game: GameConfig = GameConfig()
    
    class Config:
        env_file = ".env"


# Глобальный экземпляр настроек
settings = Settings()