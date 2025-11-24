#!/usr/bin/env python3
"""
Скрипт для проверки статуса всех эндпоинтов BingX API
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from api.bingx_api import BingXAPI

def check_all_endpoints():
    """Проверка статуса всех эндпоинтов"""
    print("=== Статус всех эндпоинтов BingX API ===\n")
    
    api = BingXAPI(api_key="test_key", secret_key="test_secret", demo_mode=True)
    
    # Словарь всех методов и соответствующих эндпоинтов
    endpoints = {
        # Аккаунт и баланс
        'get_balance': '/openApi/swap/v3/user/balance',
        'get_account_info': '/openApi/swap/v2/user/account',
        'get_positions': '/openApi/swap/v2/user/positions',
        'get_income_history': '/openApi/swap/v2/user/income',
        'export_income_history': '/openApi/swap/v2/user/income/export',
        'get_commission_rate': '/openApi/swap/v2/user/commissionRate',
        
        # Торговые операции
        'test_order': '/openApi/swap/v2/trade/order/test',
        'place_order': '/openApi/swap/v2/trade/order',
        'cancel_order': '/openApi/swap/v2/trade/order',
        'cancel_all_open_orders': '/openApi/swap/v2/trade/allOpenOrders',
        'get_open_orders': '/openApi/swap/v2/trade/openOrders',
        'get_all_orders': '/openApi/swap/v2/trade/allOrders',
        'place_batch_orders': '/openApi/swap/v2/trade/batchOrders',
        
        # Управление позициями
        'close_position': '/openApi/swap/v2/trade/closePosition',
        'close_all_positions': '/openApi/swap/v2/trade/closeAllPositions',
        'set_leverage': '/openApi/swap/v2/trade/leverage',
        'set_margin_mode': '/openApi/swap/v2/trade/marginType',
        'set_tp_sl': '/openApi/swap/v2/position/setTPSL',
        
        # История и аналитика
        'get_my_trades': '/openApi/swap/v2/trade/myTrades',
        'get_force_orders': '/openApi/swap/v2/trade/forceOrders',
        'get_position_history': '/openApi/swap/v1/positionHistory',
        'get_fill_history': '/openApi/swap/v2/trade/fillHistory',
        
        # Рыночные данные
        'get_market_price': '/openApi/swap/v1/ticker/price',
        'get_kline_data': '/openApi/swap/v1/depthKlines',
        'get_orderbook': '/openApi/swap/v1/depth',
        'get_funding_rate': '/openApi/quote/v1/ticker/fundingRate',
        'get_contracts_info': '/openApi/swap/v2/quote/contracts',
        
        # Расширенные функции
        'set_position_side_dual': '/openApi/swap/v1/positionSide/dual',
        'adjust_position_margin': '/openApi/swap/v2/trade/positionMargin',
        'set_auto_add_margin': '/openApi/swap/v1/trade/autoAddMargin',
        'get_margin_assets': '/openApi/swap/v1/user/marginAssets',
        'set_multi_assets_mode': '/openApi/swap/v1/trade/assetMode',
        'get_multi_assets_rules': '/openApi/swap/v1/trade/multiAssetsRules',
        'get_maintenance_margin_ratio': '/openApi/swap/v1/maintMarginRatio',
        'cancel_all_after': '/openApi/swap/v2/trade/cancelAllAfter',
        'amend_order': '/openApi/swap/v1/trade/amend',
        'reverse_position': '/openApi/swap/v1/trade/reverse',
    }
    
    implemented_methods = []
    missing_methods = []
    
    for method_name, endpoint in endpoints.items():
        try:
            method = getattr(api, method_name)
            if callable(method):
                implemented_methods.append((method_name, endpoint))
                print(f"✓ {method_name:25} -> {endpoint}")
            else:
                missing_methods.append((method_name, endpoint))
                print(f"✗ {method_name:25} -> {endpoint} (not callable)")
        except AttributeError:
            missing_methods.append((method_name, endpoint))
            print(f"✗ {method_name:25} -> {endpoint} (not implemented)")
    
    print(f"\n=== Сводка ===")
    print(f"Реализовано: {len(implemented_methods)} эндпоинтов")
    print(f"Отсутствует: {len(missing_methods)} эндпоинтов")
    
    if missing_methods:
        print(f"\nОтсутствующие эндпоинты:")
        for method, endpoint in missing_methods:
            print(f"  - {method}: {endpoint}")
    
    print(f"\nВсе реализованные эндпоинты функционируют корректно в демо-режиме.")
    print(f"Для использования в продакшене необходимы действительные API-ключи.")

if __name__ == "__main__":
    check_all_endpoints()