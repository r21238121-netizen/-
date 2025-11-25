"""
Correct BingX API Endpoints
Based on the verified data provided by the user
"""

# === АККАУНТ И БАЛАНС ===
ACCOUNT_ENDPOINTS = {
    'get_balance': '/openApi/swap/v3/user/balance',
    'get_positions': '/openApi/swap/v2/user/positions',
    'get_income_history': '/openApi/swap/v2/user/income',
    'get_commission_rate': '/openApi/swap/v2/user/commissionRate',
    # Примечание: /user/account — не существует
}

# === ТОРГОВЛЯ ===
TRADING_ENDPOINTS = {
    'test_order': '/openApi/swap/v2/trade/order/test',
    'place_order': '/openApi/swap/v2/trade/order',               # POST
    'cancel_order': '/openApi/swap/v2/trade/order',              # DELETE
    'cancel_all_open_orders': '/openApi/swap/v2/trade/allOpenOrders',
    'get_open_orders': '/openApi/swap/v2/trade/openOrders',
    'get_order_details': '/openApi/swap/v2/trade/order',         # GET
    'get_pending_order_status': '/openApi/swap/v2/trade/openOrder',
    'get_all_orders': '/openApi/swap/v1/trade/fullOrder',        # вся история
    'place_batch_orders': '/openApi/swap/v2/trade/batchOrders',  # POST
    'cancel_batch_orders': '/openApi/swap/v2/trade/batchOrders', # DELETE
}

# === УПРАВЛЕНИЕ ПОЗИЦИЯМИ ===
POSITION_MANAGEMENT_ENDPOINTS = {
    'close_all_positions': '/openApi/swap/v2/trade/closeAllPositions',
    'close_position_by_id': '/openApi/swap/v1/trade/closePosition',
    'set_leverage': '/openApi/swap/v2/trade/leverage',           # POST
    'get_leverage': '/openApi/swap/v2/trade/leverage',           # GET
    'set_margin_mode': '/openApi/swap/v2/trade/marginType',      # POST
    'get_margin_mode': '/openApi/swap/v2/trade/marginType',      # GET
    'adjust_isolated_margin': '/openApi/swap/v2/trade/positionMargin',
    'set_position_mode': '/openApi/swap/v1/positionSide/dual',   # POST
    'get_position_mode': '/openApi/swap/v1/positionSide/dual',   # GET
    'cancel_all_after': '/openApi/swap/v2/trade/cancelAllAfter',
    'amend_order': '/openApi/swap/v1/trade/amend',
    'reverse_position': '/openApi/swap/v1/trade/reverse',
    'cancel_replace': '/openApi/swap/v1/trade/cancelReplace',
    'batch_cancel_replace': '/openApi/swap/v1/trade/batchCancelReplace',
    'auto_add_margin': '/openApi/swap/v1/trade/autoAddMargin',
}

# === ИСТОРИЯ И АНАЛИТИКА ===
HISTORY_ENDPOINTS = {
    'get_force_orders': '/openApi/swap/v2/trade/forceOrders',
    'get_fill_history': '/openApi/swap/v2/trade/fillHistory',
    'get_all_fill_orders': '/openApi/swap/v2/trade/allFillOrders',
    'get_position_history': '/openApi/swap/v1/trade/positionHistory',
    'get_isolated_margin_history': '/openApi/swap/v1/positionMargin/history',
    'get_maintenance_margin_ratio': '/openApi/swap/v1/maintMarginRatio',
}

# === РЫНОК (публичные, не требуют подписи) ===
MARKET_ENDPOINTS = {
    'get_contracts_info': '/openApi/swap/v2/quote/contracts',
    'get_kline_data': '/openApi/swap/v2/quote/klines',
    'get_orderbook': '/openApi/swap/v2/quote/depth',
    'get_ticker': '/openApi/swap/v2/quote/ticker',
    'get_24hr_ticker': '/openApi/swap/v2/quote/ticker/24hr',
    # Примечание: отдельного эндпоинта для fundingRate нет — он в /contracts
}

# === РАСШИРЕННЫЕ ФУНКЦИИ ===
ADVANCED_ENDPOINTS = {
    'get_vst': '/openApi/swap/v1/trade/getVst',                  # демо-баланс
    'set_asset_mode': '/openApi/swap/v1/trade/assetMode',        # POST
    'get_asset_mode': '/openApi/swap/v1/trade/assetMode',        # GET
    'get_multi_assets_rules': '/openApi/swap/v1/trade/multiAssetsRules',  # без ключа
    'get_margin_assets': '/openApi/swap/v1/user/marginAssets',
}

# === TWAP (алгоритмические ордера) ===
TWAP_ENDPOINTS = {
    'place_twap_order': '/openApi/swap/v1/twap/order',
    'get_twap_open_orders': '/openApi/swap/v1/twap/openOrders',
    'get_twap_history_orders': '/openApi/swap/v1/twap/historyOrders',
    'get_twap_order_detail': '/openApi/swap/v1/twap/orderDetail',
    'cancel_twap_order': '/openApi/swap/v1/twap/cancelOrder',
}

# All endpoints combined
ALL_ENDPOINTS = {
    **ACCOUNT_ENDPOINTS,
    **TRADING_ENDPOINTS,
    **POSITION_MANAGEMENT_ENDPOINTS,
    **HISTORY_ENDPOINTS,
    **MARKET_ENDPOINTS,
    **ADVANCED_ENDPOINTS,
    **TWAP_ENDPOINTS
}

# HTTP methods for endpoints that require specific methods
ENDPOINT_METHODS = {
    # POST endpoints
    'place_order': 'POST',
    'cancel_order': 'DELETE',  # Note: cancel_order is DELETE
    'cancel_all_open_orders': 'DELETE',
    'place_batch_orders': 'POST',
    'cancel_batch_orders': 'DELETE',
    'set_leverage': 'POST',
    'set_margin_mode': 'POST',
    'set_position_mode': 'POST',
    'cancel_all_after': 'POST',
    'amend_order': 'POST',
    'reverse_position': 'POST',
    'cancel_replace': 'POST',
    'batch_cancel_replace': 'POST',
    'auto_add_margin': 'POST',
    'set_asset_mode': 'POST',
    
    # GET endpoints (default, but explicitly defined for clarity)
    'get_balance': 'GET',
    'get_positions': 'GET',
    'get_income_history': 'GET',
    'get_commission_rate': 'GET',
    'get_open_orders': 'GET',
    'get_order_details': 'GET',
    'get_pending_order_status': 'GET',
    'get_all_orders': 'GET',
    'get_leverage': 'GET',
    'get_margin_mode': 'GET',
    'get_position_mode': 'GET',
    'get_force_orders': 'GET',
    'get_fill_history': 'GET',
    'get_all_fill_orders': 'GET',
    'get_position_history': 'GET',
    'get_isolated_margin_history': 'GET',
    'get_maintenance_margin_ratio': 'GET',
    'get_contracts_info': 'GET',
    'get_kline_data': 'GET',
    'get_orderbook': 'GET',
    'get_ticker': 'GET',
    'get_24hr_ticker': 'GET',
    'get_asset_mode': 'GET',
    'get_multi_assets_rules': 'GET',
    'get_margin_assets': 'GET',
    'get_vst': 'GET',
    'get_twap_open_orders': 'GET',
    'get_twap_history_orders': 'GET',
    'get_twap_order_detail': 'GET',
    
    # Additional endpoints
    'test_order': 'POST',
    'place_twap_order': 'POST',
    'cancel_twap_order': 'DELETE',
}