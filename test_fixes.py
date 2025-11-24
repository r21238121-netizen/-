#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправленного приложения
"""
import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt6.QtWidgets import QApplication
from src.main import FuturesScoutApp

def test_demo_mode():
    """Тестирование демо-режима"""
    print("Запуск теста демо-режима...")
    
    try:
        app = FuturesScoutApp()
        
        # Запускаем в демо-режиме напрямую
        app.api = None  # Имитируем отсутствие API
        app.ai_agent = None  # Имитируем отсутствие ИИ агента
        
        # Создаем API в демо-режиме
        from src.api.bingx_api import BingXAPI
        app.api = BingXAPI(demo_mode=True)
        
        # Создаем ИИ агента в демо-режиме
        from src.models.ai_agent import AIAgent
        app.ai_agent = AIAgent(app.api, demo_mode=True)
        
        # Запускаем основное окно
        app.start_main_window(real_mode=False)
        
        print("Демо-режим успешно запущен")
        return True
    except Exception as e:
        print(f"Ошибка при запуске демо-режима: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_demo_mode()