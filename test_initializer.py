#!/usr/bin/env python3
"""
Тестирование модуля инициализации BingX API без ввода ключей
"""
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.bingx_initializer import BingXInitializer

def test_initializer_structure():
    """Тестирование структуры инициализатора"""
    print("=== Тестирование структуры BingXInitializer ===")
    
    # Создаем инициализатор с фиктивными ключами
    initializer = BingXInitializer("fake_api_key", "fake_secret_key")
    
    # Проверяем наличие основных методов
    methods = [
        'validate_credentials',
        'get_balance', 
        'get_positions',
        'get_account_info',
        'get_contracts_info',
        'initialize_and_check_criteria'
    ]
    
    for method in methods:
        if hasattr(initializer, method):
            print(f"✅ Метод {method} доступен")
        else:
            print(f"❌ Метод {method} отсутствует")
    
    print("\n=== Тестирование завершено ===")

if __name__ == "__main__":
    test_initializer_structure()