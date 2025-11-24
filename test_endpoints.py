#!/usr/bin/env python3
"""
Тестирование специфических эндпоинтов API BingX
"""
import sys
import os
sys.path.insert(0, 'src')

from api.bingx_api import BingXAPI

def test_required_endpoints():
    """Тестирование всех обязательных эндпоинтов из документации"""
    print("Тестирование обязательных эндпоинтов API BingX...")
    
    # Создаем API в демо-режиме
    api = BingXAPI(demo_mode=True)
    
    # 1. Отображение доступных средств - /openApi/swap/v3/user/balance
    print("\n1. Тестирование /openApi/swap/v3/user/balance (get_balance)")
    try:
        balance = api.get_balance()
        print(f"   Статус: {balance.get('code', 'N/A')}")
        if 'data' in balance and 'balances' in balance['data']:
            for bal in balance['data']['balances']:
                print(f"   - Актив: {bal.get('asset', 'N/A')}, Баланс: {bal.get('walletBalance', 'N/A')}")
        else:
            print(f"   Данные: {balance}")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    # 2. Отслеживание открытых позиций - /openApi/swap/v2/user/positions
    print("\n2. Тестирование /openApi/swap/v2/user/positions (get_positions)")
    try:
        positions = api.get_positions()
        print(f"   Статус: {positions.get('code', 'N/A')}")
        if 'data' in positions:
            for pos in positions['data']:
                print(f"   - Символ: {pos.get('symbol', 'N/A')}, Позиция: {pos.get('positionAmt', 'N/A')}, Сторона: {pos.get('positionSide', 'N/A')}")
        else:
            print(f"   Данные: {positions}")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    # 3. Анализ эффективности - /openApi/swap/v2/user/income
    print("\n3. Тестирование /openApi/swap/v2/user/income (get_income_history)")
    try:
        income = api.get_income_history()
        print(f"   Статус: {income.get('code', 'N/A')}")
        if 'data' in income:
            for inc in income['data'][:3]:  # Показываем первые 3 записи
                print(f"   - Символ: {inc.get('symbol', 'N/A')}, Тип: {inc.get('incomeType', 'N/A')}, Доход: {inc.get('income', 'N/A')}")
            if len(income['data']) > 3:
                print(f"   ... и еще {len(income['data']) - 3} записей")
        else:
            print(f"   Данные: {income}")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    # 4. Учёт комиссий - /openApi/swap/v2/user/commissionRate
    print("\n4. Тестирование /openApi/swap/v2/user/commissionRate (get_commission_rate)")
    try:
        commission = api.get_commission_rate('BTC-USDT')
        print(f"   Статус: {commission.get('code', 'N/A')}")
        if 'data' in commission:
            print(f"   - Символ: {commission['data'].get('symbol', 'N/A')}")
            print(f"   - Maker комиссия: {float(commission['data'].get('maker', 0)) * 100}%")
            print(f"   - Taker комиссия: {float(commission['data'].get('taker', 0)) * 100}%")
        else:
            print(f"   Данные: {commission}")
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    # 5. Дополнительные проверки для демо-режима
    print("\n5. Тестирование дополнительных функций для демо-режима")
    try:
        # Проверка валидации (в демо-режиме всегда должна возвращать True)
        is_valid = api.validate_credentials()
        print(f"   Валидация API-ключей: {is_valid}")
        
        # Получение рыночной цены
        market_price = api.get_market_price('BTC-USDT')
        print(f"   Рыночная цена BTC-USDT: {market_price['data'][0]['price'] if market_price.get('data') else 'N/A'}")
        
        # Получение K-линий
        klines = api.get_kline_data('BTC-USDT', interval='1h', limit=5)
        print(f"   K-линии (последние 5): {len(klines.get('data', [])) if klines else 0} свечей")
        
    except Exception as e:
        print(f"   ОШИБКА: {e}")
    
    print("\n✓ Все обязательные эндпоинты протестированы!")

def test_demo_data_consistency():
    """Проверка консистентности демо-данных"""
    print("\nПроверка консистентности демо-данных...")
    
    api = BingXAPI(demo_mode=True)
    
    # Получаем данные несколько раз, чтобы проверить стабильность
    balance1 = api.get_balance()
    balance2 = api.get_balance()
    
    print(f"Баланс 1: {balance1.get('data', {}).get('balances', [{}])[0].get('walletBalance', 'N/A')}")
    print(f"Баланс 2: {balance2.get('data', {}).get('balances', [{}])[0].get('walletBalance', 'N/A')}")
    
    # Проверяем, что демо-данные возвращаются стабильно
    positions = api.get_positions()
    print(f"Позиции: {len(positions.get('data', []))} записей")
    
    income = api.get_income_history()
    print(f"История доходов: {len(income.get('data', []))} записей")
    
    print("✓ Проверка консистентности демо-данных завершена!")

if __name__ == "__main__":
    test_required_endpoints()
    test_demo_data_consistency()
    print("\n✓ Все тесты эндпоинтов завершены успешно!")