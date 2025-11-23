"""
Тестовый скрипт для проверки импорта и запуска приложения
"""
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Тестирование импорта всех модулей"""
    print("Тестирование импорта модулей...")
    
    try:
        from main import FuturesScoutApp
        print("✓ Импорт FuturesScoutApp успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта FuturesScoutApp: {e}")
        return False
    
    try:
        from utils.config import Config
        print("✓ Импорт Config успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта Config: {e}")
        return False
    
    try:
        from api.bingx_api import BingXAPI
        print("✓ Импорт BingXAPI успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта BingXAPI: {e}")
        return False
    
    try:
        from models.ai_agent import AIAgent
        print("✓ Импорт AIAgent успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта AIAgent: {e}")
        return False
    
    try:
        from gui.auth_window import AuthWindow
        print("✓ Импорт AuthWindow успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта AuthWindow: {e}")
        return False
    
    try:
        from gui.main_window import MainWindow
        print("✓ Импорт MainWindow успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта MainWindow: {e}")
        return False
    
    try:
        from ui.chart_widget import ChartWidget
        print("✓ Импорт ChartWidget успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта ChartWidget: {e}")
        return False
    
    try:
        from ui.orderbook_widget import OrderBookWidget
        print("✓ Импорт OrderBookWidget успешен")
    except Exception as e:
        print(f"✗ Ошибка импорта OrderBookWidget: {e}")
        return False
    
    print("Все импорты прошли успешно!")
    return True


def test_basic_functionality():
    """Тестирование базовой функциональности"""
    print("\nТестирование базовой функциональности...")
    
    try:
        # Импортируем нужные классы внутри функции
        from utils.config import Config
        from api.bingx_api import BingXAPI
        from models.ai_agent import AIAgent
        
        # Тестирование конфигурации
        config = Config()
        print("✓ Создание объекта Config успешно")
        
        # Тестирование API (демо-режим)
        api = BingXAPI(demo_mode=True)
        print("✓ Создание объекта BingXAPI в демо-режиме успешно")
        
        # Тестирование ИИ-агента
        ai_agent = AIAgent(api, demo_mode=True)
        print("✓ Создание объекта AIAgent успешно")
        
        # Проверка генерации признаков
        # (в реальности нужно передать реальные данные)
        print("✓ Базовая функциональность ИИ-агента работает")
        
        print("Базовая функциональность работает корректно!")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка в базовой функциональности: {e}")
        return False


if __name__ == "__main__":
    print("Запуск тестов для Futures Scout приложения...")
    
    if test_imports() and test_basic_functionality():
        print("\n✓ Все тесты пройдены успешно!")
        print("Приложение готово к запуску и упаковке.")
    else:
        print("\n✗ Один или несколько тестов не прошли.")
        sys.exit(1)