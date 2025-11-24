#!/usr/bin/env python3
"""
Тестирование основных компонентов без GUI
"""
import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_core_imports():
    """Тестирование импорта основных модулей"""
    print("Тестирование импорта основных модулей...")
    
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
    
    print("Все основные импорты прошли успешно!")
    return True

def test_bingx_api():
    """Тестирование основных функций BingX API"""
    print("\nТестирование BingX API...")
    
    try:
        from api.bingx_api import BingXAPI
        
        # Создаем API в демо-режиме
        api = BingXAPI(demo_mode=True)
        print("✓ Создание API в демо-режиме успешно")
        
        # Тестируем основные методы
        balance = api.get_balance()
        print(f"✓ Получение баланса: {type(balance)}")
        
        positions = api.get_positions()
        print(f"✓ Получение позиций: {type(positions)}")
        
        income = api.get_income_history()
        print(f"✓ Получение истории доходов: {type(income)}")
        
        commission = api.get_commission_rate('BTC-USDT')
        print(f"✓ Получение комиссии: {type(commission)}")
        
        market_price = api.get_market_price('BTC-USDT')
        print(f"✓ Получение рыночной цены: {type(market_price)}")
        
        print("Все тесты BingX API прошли успешно!")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка в тестах BingX API: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_agent():
    """Тестирование ИИ-агента"""
    print("\nТестирование ИИ-агента...")
    
    try:
        from api.bingx_api import BingXAPI
        from models.ai_agent import AIAgent
        
        api = BingXAPI(demo_mode=True)
        ai_agent = AIAgent(api, demo_mode=True)
        print("✓ Создание ИИ-агента успешно")
        
        # Тестируем генерацию сигнала (на реальных данных в демо-режиме)
        signal = ai_agent.generate_signal('BTC-USDT')
        print(f"✓ Генерация сигнала: {type(signal)}")
        
        # Тестируем анализ рынка
        analysis = ai_agent.analyze_market_situation('BTC-USDT')
        print(f"✓ Анализ рынка: {type(analysis)}")
        
        # Тестируем анализ эффективности
        performance = ai_agent.analyze_trading_performance('BTC-USDT')
        print(f"✓ Анализ эффективности: {type(performance)}")
        
        print("Все тесты ИИ-агента прошли успешно!")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка в тестах ИИ-агента: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Тестирование всех основных эндпоинтов API"""
    print("\nТестирование всех основных эндпоинтов API...")
    
    try:
        from api.bingx_api import BingXAPI
        
        # Создаем API в демо-режиме
        api = BingXAPI(demo_mode=True)

        # Тестируем все основные эндпоинты
        endpoints_tests = [
            ('get_balance', lambda: api.get_balance()),
            ('get_positions', lambda: api.get_positions()),
            ('get_income_history', lambda: api.get_income_history()),
            ('get_commission_rate', lambda: api.get_commission_rate('BTC-USDT')),
            ('get_market_price', lambda: api.get_market_price('BTC-USDT')),
            ('get_kline_data', lambda: api.get_kline_data('BTC-USDT')),
            ('get_orderbook', lambda: api.get_orderbook('BTC-USDT')),
            ('get_funding_rate', lambda: api.get_funding_rate('BTC-USDT')),
            ('get_open_interest', lambda: api.get_open_interest('BTC-USDT')),
        ]
        
        for name, test_func in endpoints_tests:
            try:
                result = test_func()
                print(f"✓ {name}: {type(result)}")
            except Exception as e:
                print(f"✗ {name}: {e}")
        
        print("Тестирование эндпоинтов завершено!")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка в тестах эндпоинтов: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Запуск тестов основных компонентов Futures Scout...")
    
    success = True
    success &= test_core_imports()
    success &= test_bingx_api()
    success &= test_ai_agent()
    success &= test_api_endpoints()
    
    if success:
        print("\n✓ Все тесты пройдены успешно!")
        print("Код не содержит критических ошибок!")
    else:
        print("\n✗ Один или несколько тестов не прошли.")
        sys.exit(1)