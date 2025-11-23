import asyncio
import logging
from telegram.ext import Application
import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response

from src.core.di import container
from src.core.config import settings
from src.adapters.telegram_handler import TelegramHandler
from src.monitoring.logging import setup_logging, log
from src.monitoring.metrics import REQUESTS_TOTAL


# Настройка логирования
setup_logging()


async def setup_telegram_bot():
    """Настройка и запуск Telegram бота"""
    # Создаем приложение Telegram
    application = Application.builder().token(settings.telegram_token).build()
    
    # Получаем зависимости из DI контейнера
    telegram_handler = container.telegram_handler()
    
    # Настраиваем обработчики
    telegram_handler.setup_handlers(application)
    
    log.info("Telegram bot initialized", bot_token_hash=hash(settings.telegram_token))
    
    # Запускаем бота
    await application.run_polling()


def create_api_app():
    """Создание FastAPI приложения для мониторинга и метрик"""
    app = FastAPI(title="Phoenix Bot API", version="1.0.0")
    
    @app.get("/")
    def read_root():
        return {"status": "running", "service": "phoenix_bot"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "timestamp": "now"}
    
    @app.get("/metrics")
    def get_metrics():
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    
    return app


async def main():
    """Основная точка входа"""
    log.info("Starting Phoenix Bot", version="1.0.0")
    
    # Инициализация базы данных
    await container.database().init_db()
    log.info("Database initialized")
    
    # Запуск Telegram бота
    await setup_telegram_bot()


if __name__ == "__main__":
    # Запуск основного приложения
    asyncio.run(main())