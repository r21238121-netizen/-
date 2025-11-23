import structlog
from typing import Any, Dict
from datetime import datetime


# Настройка structlog
def setup_logging():
    """Настройка логирования с использованием structlog"""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# Глобальный логгер
logger = structlog.get_logger()


class Logger:
    """Класс для структурированного логирования"""
    
    def __init__(self):
        self.logger = logger
    
    def info(self, message: str, **kwargs):
        """Логирование информационных сообщений"""
        self.logger.info(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Логирование ошибок"""
        self.logger.error(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Логирование предупреждений"""
        self.logger.warning(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Логирование отладочных сообщений"""
        self.logger.debug(message, **kwargs)
    
    def game_event(self, event_type: str, user_id: str, game_id: str, **kwargs):
        """Логирование игровых событий"""
        self.logger.info(
            "Game event",
            event_type=event_type,
            user_id=user_id,
            game_id=game_id,
            **kwargs
        )
    
    def admin_action(self, action: str, admin_id: str, target_id: str, **kwargs):
        """Логирование административных действий"""
        self.logger.info(
            "Admin action",
            action=action,
            admin_id=admin_id,
            target_id=target_id,
            **kwargs
        )
    
    def user_action(self, action: str, user_id: str, **kwargs):
        """Логирование действий пользователя"""
        self.logger.info(
            "User action",
            action=action,
            user_id=user_id,
            **kwargs
        )


# Глобальный экземпляр логгера
log = Logger()