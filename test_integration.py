#!/usr/bin/env python3
"""
Тестирование интеграции нового инициализатора с основным приложением
"""
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Тестирование импортов"""
    print("=== Тестирование импортов ===")
    
    try:
        from api.bingx_api import BingXAPI
        print("✅ BingXAPI импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта BingXAPI: {e}")
    
    try:
        from api.bingx_initializer import BingXInitializer, initialize_bingx_connection
        print("✅ BingXInitializer и initialize_bingx_connection импортированы успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта инициализатора: {e}")
    
    try:
        from api.bingx_initializer import initialize_bingx_connection
        print("✅ initialize_bingx_connection импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта initialize_bingx_connection: {e}")
    
    try:
        from src.main import FuturesScoutApp
        print("✅ FuturesScoutApp импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта FuturesScoutApp: {e}")

def test_initializer_functionality():
    """Тестирование функциональности инициализатора"""
    print("\n=== Тестирование функциональности инициализатора ===")
    
    try:
        from api.bingx_initializer import BingXInitializer
        
        # Создаем инициализатор с фиктивными ключами
        initializer = BingXInitializer("fake_api_key", "fake_secret_key")
        
        # Проверяем, что все основные методы существуют и имеют правильную сигнатуру
        methods_with_expected_params = {
            'validate_credentials': 0,  # без параметров
            'get_balance': 0,
            'get_positions': 0,
            'get_account_info': 0,
            'get_contracts_info': 0,
            'initialize_and_check_criteria': 0,
        }
        
        for method_name, expected_params in methods_with_expected_params.items():
            method = getattr(initializer, method_name)
            import inspect
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            # Убираем 'self' из подсчета
            actual_params = len(params) - 1 if params and params[0] == 'self' else len(params)
            
            if actual_params == expected_params:
                print(f"✅ Метод {method_name} имеет правильную сигнатуру")
            else:
                print(f"❌ Метод {method_name} имеет неправильную сигнатуру: ожидается {expected_params}, получено {actual_params}")
        
        print("✅ Функциональность инициализатора протестирована")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования функциональности инициализатора: {e}")

def test_main_integration():
    """Тестирование интеграции с main.py"""
    print("\n=== Тестирование интеграции с main.py ===")
    
    try:
        # Проверим, что в main.py есть нужные импорты
        import src.main
        import importlib
        importlib.reload(src.main)  # Перезагружаем модуль
        
        # Проверим, что модуль загрузился без ошибок
        print("✅ Модуль main.py загружен без ошибок")
        
        # Проверим, что класс FuturesScoutApp существует
        from src.main import FuturesScoutApp
        app = FuturesScoutApp()
        print("✅ FuturesScoutApp создан успешно")
        
        # Проверим, что методы существуют
        required_methods = [
            'run',
            'initialize_and_check_criteria',
            'connect_with_credentials',
            'start_auth_window',
            'start_main_window'
        ]
        
        for method in required_methods:
            if hasattr(app, method):
                print(f"✅ Метод {method} доступен в FuturesScoutApp")
            else:
                print(f"❌ Метод {method} отсутствует в FuturesScoutApp")
        
    except Exception as e:
        print(f"❌ Ошибка тестирования интеграции: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
    test_initializer_functionality()
    test_main_integration()
    print("\n=== Тестирование интеграции завершено ===")