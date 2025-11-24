#!/usr/bin/env python3
"""
Демонстрационный скрипт для показа работы системы инициализации API
"""
import asyncio
from api_initializer import initialize_apis

async def demo():
    print("=== Демонстрация системы инициализации API ===")
    print("Используем фиктивные ключи для демонстрации...")
    
    # Фиктивные ключи для демонстрации
    fake_keys = {
        "openai": "fake_openai_key",
        "anthropic": "fake_anthropic_key", 
        "google": "fake_google_key",
        "cohere": "fake_cohere_key",
        "huggingface": "fake_huggingface_key"
    }
    
    from api_initializer import ApiChecker, get_endpoints_config
    
    # Создаем экземпляр проверяльщика API
    checker = ApiChecker(fake_keys)
    
    print("Начинаем проверку API-эндпоинтов... (максимум 2 минуты)")
    
    # Получаем конфигурацию эндпоинтов
    endpoints_config = get_endpoints_config()
    
    # Выполняем проверку всех API
    results = await checker.check_all_apis(endpoints_config)
    
    # Выводим результаты
    print(f"\nРаботающие API: {list(results['working'].keys())}")
    print(f"Неработающие API: {list(results['failed'].keys())}")
    
    # Сохраняем неработающие API в файл
    checker.save_failed_apis()
    
    if results['working']:
        print("\nИнициализация завершена успешно!")
        print("Система готова использовать рабочие API для основной работы.")
        return results['working']
    else:
        print("\nНе найдено ни одного рабочего API.")
        return None

if __name__ == "__main__":
    working_apis = asyncio.run(demo())
    if working_apis:
        print(f"\nДемонстрация завершена. Работающие API: {list(working_apis.keys())}")
    else:
        print("\nДемонстрация завершена. Нет рабочих API.")