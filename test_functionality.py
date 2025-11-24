#!/usr/bin/env python3
"""
Тестирование основных функций приложения без GUI
"""
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.ai_agent import AIAgent
from api.bingx_api import BingXAPI
from utils.config import Config


def test_functionality():
    print("Тестирование основных функций Futures Scout...")
    
    # Тестируем конфигурацию
    print("\n1. Тестирование конфигурации...")
    config = Config()
    print(f"Директория конфигурации: {config.config_dir}")
    print(f"Есть сохраненные ключи: {config.has_saved_credentials()}")
    
    # Тестируем API (в демо-режиме)
    print("\n2. Тестирование API (демо-режим)...")
    api = BingXAPI(demo_mode=True)
    print("API создан в демо-режиме")
    
    # Тестируем получение демо-данных
    try:
        balance_data = api.get_balance()
        print(f"Баланс (демо): {balance_data}")
    except Exception as e:
        print(f"Ошибка получения баланса: {e}")
    
    # Тестируем ИИ-агента
    print("\n3. Тестирование ИИ-агента...")
    ai_agent = AIAgent(api, demo_mode=True)
    print("ИИ-агент создан")
    
    # Тестируем анализ рынка
    try:
        analysis = ai_agent.analyze_market_situation('BTC-USDT')
        print(f"Анализ рынка для BTC-USDT:\n{analysis}")
    except Exception as e:
        print(f"Ошибка анализа рынка: {e}")
    
    # Тестируем генерацию сигнала (в демо-режиме)
    try:
        signal = ai_agent.generate_signal('BTC-USDT')
        print(f"Сигнал: {signal}")
    except Exception as e:
        print(f"Ошибка генерации сигнала: {e}")
    
    # Тестируем статистику
    try:
        stats = ai_agent.get_performance_stats()
        print(f"Статистика ИИ: {stats}")
    except Exception as e:
        print(f"Ошибка получения статистики: {e}")
    
    print("\n4. Тестирование новых функций...")
    
    # Тестируем функцию озвучивания анализа
    try:
        speak_text = ai_agent.speak_analysis('ETH-USDT')
        print(f"Текст для озвучивания анализа:\n{speak_text}")
    except Exception as e:
        print(f"Ошибка озвучивания анализа: {e}")
    
    # Тестируем получение внешних данных
    try:
        external_data = ai_agent._get_external_market_data('BTC-USDT')
        print(f"Внешние данные получены: {external_data is not None}")
    except Exception as e:
        print(f"Ошибка получения внешних данных: {e}")
    
    print("\nВсе тесты завершены успешно!")


if __name__ == "__main__":
    test_functionality()