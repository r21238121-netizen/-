#!/usr/bin/env python3
"""
Тестирование всех эндпоинтов BingX API
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.bingx_api import BingXAPI

def test_all_endpoints():
    """Тестирование всех эндпоинтов API"""
    # Используем демо-режим для тестирования
    api = BingXAPI(api_key="test_key", secret_key="test_secret", demo_mode=True)
    
    print("=== Тестирование всех эндпоинтов BingX API ===\n")
    
    # Тестирование эндпоинтов аккаунта и баланса
    print("1. Тестирование эндпоинтов аккаунта и баланса:")
    try:
        balance = api.get_balance()
        print(f"   ✓ get_balance(): {balance['code']}")
    except Exception as e:
        print(f"   ✗ get_balance(): {e}")
    
    try:
        account_info = api.get_account_info()
        print(f"   ✓ get_account_info(): {account_info['code']}")
    except Exception as e:
        print(f"   ✗ get_account_info(): {e}")
    
    try:
        positions = api.get_positions()
        print(f"   ✓ get_positions(): {positions['code']}")
    except Exception as e:
        print(f"   ✗ get_positions(): {e}")
    
    # Тестирование эндпоинтов торговли
    print("\n2. Тестирование эндпоинтов торговли:")
    try:
        test_order_result = api.test_order("BTC-USDT", "BUY", "LIMIT", "0.001", "60000")
        print(f"   ✓ test_order(): {test_order_result['code']}")
    except Exception as e:
        print(f"   ✗ test_order(): {e}")
    
    try:
        order = api.place_order("BTC-USDT", "BUY", "0.001", "LIMIT", "60000")
        print(f"   ✓ place_order(): {order['code']}")
    except Exception as e:
        print(f"   ✗ place_order(): {e}")
    
    try:
        cancel_result = api.cancel_order("BTC-USDT", "123456")
        print(f"   ✓ cancel_order(): {cancel_result['code']}")
    except Exception as e:
        print(f"   ✗ cancel_order(): {e}")
    
    # Тестирование эндпоинтов позиций
    print("\n3. Тестирование эндпоинтов позиций:")
    try:
        close_pos = api.close_position("BTC-USDT")
        print(f"   ✓ close_position(): {close_pos['code']}")
    except Exception as e:
        print(f"   ✗ close_position(): {e}")
    
    try:
        close_all = api.close_all_positions()
        print(f"   ✓ close_all_positions(): {close_all['code']}")
    except Exception as e:
        print(f"   ✗ close_all_positions(): {e}")
    
    try:
        leverage = api.set_leverage("BTC-USDT", 10)
        print(f"   ✓ set_leverage(): {leverage['code']}")
    except Exception as e:
        print(f"   ✗ set_leverage(): {e}")
    
    try:
        margin_mode = api.set_margin_mode("BTC-USDT", "ISOLATED")
        print(f"   ✓ set_margin_mode(): {margin_mode['code']}")
    except Exception as e:
        print(f"   ✗ set_margin_mode(): {e}")
    
    # Тестирование эндпоинтов истории
    print("\n4. Тестирование эндпоинтов истории:")
    try:
        income = api.get_income_history()
        print(f"   ✓ get_income_history(): {income['code']}")
    except Exception as e:
        print(f"   ✗ get_income_history(): {e}")
    
    try:
        export_income = api.export_income_history()
        print(f"   ✓ export_income_history(): {export_income['code']}")
    except Exception as e:
        print(f"   ✗ export_income_history(): {e}")
    
    try:
        trades = api.get_my_trades("BTC-USDT")
        print(f"   ✓ get_my_trades(): {trades['code']}")
    except Exception as e:
        print(f"   ✗ get_my_trades(): {e}")
    
    try:
        fill_history = api.get_fill_history("BTC-USDT")
        print(f"   ✓ get_fill_history(): {fill_history['code']}")
    except Exception as e:
        print(f"   ✗ get_fill_history(): {e}")
    
    # Тестирование эндпоинтов комиссий
    print("\n5. Тестирование эндпоинтов комиссий:")
    try:
        commission = api.get_commission_rate("BTC-USDT")
        print(f"   ✓ get_commission_rate(): {commission['code']}")
    except Exception as e:
        print(f"   ✗ get_commission_rate(): {e}")
    
    # Тестирование рыночных эндпоинтов
    print("\n6. Тестирование рыночных эндпоинтов:")
    try:
        market_price = api.get_market_price("BTC-USDT")
        print(f"   ✓ get_market_price(): {market_price['code']}")
    except Exception as e:
        print(f"   ✗ get_market_price(): {e}")
    
    try:
        contracts = api.get_contracts_info()
        print(f"   ✓ get_contracts_info(): {contracts['code']}")
    except Exception as e:
        print(f"   ✗ get_contracts_info(): {e}")
    
    # Тестирование дополнительных эндпоинтов
    print("\n7. Тестирование дополнительных эндпоинтов:")
    try:
        force_orders = api.get_force_orders()
        print(f"   ✓ get_force_orders(): {force_orders['code']}")
    except Exception as e:
        print(f"   ✗ get_force_orders(): {e}")
    
    try:
        pos_history = api.get_position_history("BTC-USDT")
        print(f"   ✓ get_position_history(): {pos_history['code']}")
    except Exception as e:
        print(f"   ✗ get_position_history(): {e}")
    
    try:
        maint_margin = api.get_maintenance_margin_ratio("BTC-USDT")
        print(f"   ✓ get_maintenance_margin_ratio(): {maint_margin['code']}")
    except Exception as e:
        print(f"   ✗ get_maintenance_margin_ratio(): {e}")
    
    print("\n=== Тестирование завершено ===")

if __name__ == "__main__":
    test_all_endpoints()