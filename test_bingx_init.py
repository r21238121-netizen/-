#!/usr/bin/env python3
"""
Тестовый скрипт для проверки нового модуля инициализации BingX API
"""
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.bingx_initializer import initialize_bingx_connection

def test_initialization():
    print("=== Тестирование инициализации BingX API ===")
    print("Введите ваши API-ключи для тестирования:")
    
    api_key = input("API Key: ").strip()
    secret_key = input("Secret Key: ").strip()
    
    if not api_key or not secret_key:
        print("Ошибка: Необходимо ввести оба ключа")
        return
    
    print("\nНачинаем инициализацию...")
    result = initialize_bingx_connection(api_key, secret_key)
    
    if result['success']:
        print("\n=== Результат инициализации ===")
        print(f"Баланс: {result['balance']} USDT")
        print(f"Монет с балансом > 0: {result['total_coins_with_balance']}")
        print(f"Открытых позиций: {result['open_positions']}")
        print(f"Активных контрактов: {result['active_contracts']}")
        print("✅ Инициализация прошла успешно!")
    else:
        print(f"\n❌ Ошибка инициализации: {result['error']}")

if __name__ == "__main__":
    test_initialization()