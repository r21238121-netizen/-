# BingX API Endpoints Documentation

## Overview
This document provides comprehensive information about all available endpoints in the BingX API wrapper, including their usage, parameters, and response formats.

## Base URL
- **Production**: `https://open-api.bingx.com`
- **WebSocket**: `wss://open-api-swap.bingx.com/swap-market`

## Authentication
All authenticated endpoints require:
- API Key (header: `X-BX-APIKEY`)
- Timestamp parameter
- Signature (HMAC-SHA256)

## Account & Balance Endpoints

### 1. Get Balance
- **Endpoint**: `/openApi/swap/v3/user/balance`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get account balance information
- **Function**: `get_balance()`

### 2. Get Account Info
- **Endpoint**: `/openApi/swap/v2/user/account`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get account information (margin mode, leverage, etc.)
- **Function**: `get_account_info()`

### 3. Get Positions
- **Endpoint**: `/openApi/swap/v2/user/positions`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get current open positions
- **Function**: `get_positions(symbol=None)`

## Trading Endpoints

### 4. Test Order
- **Endpoint**: `/openApi/swap/v2/trade/order/test`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Test order parameters without execution
- **Function**: `test_order(symbol, side, order_type, quantity, price=None, position_side='BOTH')`

### 5. Place Order
- **Endpoint**: `/openApi/swap/v2/trade/order`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Place a new order
- **Function**: `place_order(symbol, side, quantity, order_type='LIMIT', price=None, position_side='BOTH')`

### 6. Cancel Order
- **Endpoint**: `/openApi/swap/v2/trade/order`
- **Method**: `DELETE`
- **Authentication**: Required
- **Description**: Cancel an existing order
- **Function**: `cancel_order(symbol, order_id)`

### 7. Cancel All Orders
- **Endpoint**: `/openApi/swap/v2/trade/allOpenOrders`
- **Method**: `DELETE`
- **Authentication**: Required
- **Description**: Cancel all open orders for a symbol
- **Function**: `cancel_all_open_orders(symbol)`

### 8. Get Open Orders
- **Endpoint**: `/openApi/swap/v2/trade/openOrders`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get list of open orders
- **Function**: `get_open_orders(symbol=None)`

## Position Management Endpoints

### 9. Close Position
- **Endpoint**: `/openApi/swap/v2/trade/closePosition`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Close position with market order
- **Function**: `close_position(symbol, position_side='BOTH')`

### 10. Close All Positions
- **Endpoint**: `/openApi/swap/v2/trade/closeAllPositions`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Close all positions
- **Function**: `close_all_positions()`

### 11. Set Leverage
- **Endpoint**: `/openApi/swap/v2/trade/leverage`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Set leverage for a symbol
- **Function**: `set_leverage(symbol, leverage, position_side='BOTH')`

### 12. Set Margin Mode
- **Endpoint**: `/openApi/swap/v2/trade/marginType`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Set margin mode (cross/isolated)
- **Function**: `set_margin_mode(symbol, margin_mode)`

## History & Income Endpoints

### 13. Get Income History
- **Endpoint**: `/openApi/swap/v2/user/income`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get income history (PnL, funding fees, etc.)
- **Function**: `get_income_history(symbol=None, income_type=None, start_time=None, end_time=None, limit=1000)`

### 14. Export Income History
- **Endpoint**: `/openApi/swap/v2/user/income/export`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Export income history to Excel
- **Function**: `export_income_history(symbol=None, income_type=None, start_time=None, end_time=None)`

### 15. Get My Trades
- **Endpoint**: `/openApi/swap/v2/trade/myTrades`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get trade history
- **Function**: `get_my_trades(symbol, limit=500)`

### 16. Get Fill History
- **Endpoint**: `/openApi/swap/v2/trade/fillHistory`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get order fill history
- **Function**: `get_fill_history(symbol, start_time=None, end_time=None, limit=100)`

### 17. Get Position History
- **Endpoint**: `/openApi/swap/v1/positionHistory`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get position history
- **Function**: `get_position_history(symbol, start_time=None, end_time=None, limit=50)`

## Commission & Fee Endpoints

### 18. Get Commission Rate
- **Endpoint**: `/openApi/swap/v2/user/commissionRate`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get current commission rates
- **Function**: `get_commission_rate(symbol)`

## Market Data Endpoints

### 19. Get Market Price
- **Endpoint**: `/openApi/swap/v1/ticker/price`
- **Method**: `GET`
- **Authentication**: Not Required
- **Description**: Get current market price
- **Function**: `get_market_price(symbol)`

### 20. Get Kline Data
- **Endpoint**: `/openApi/swap/v1/depthKlines`
- **Method**: `GET`
- **Authentication**: Not Required
- **Description**: Get historical candlestick data
- **Function**: `get_kline_data(symbol, interval='1h', limit=100)`

### 21. Get Orderbook
- **Endpoint**: `/openApi/swap/v1/depth`
- **Method**: `GET`
- **Authentication**: Not Required
- **Description**: Get orderbook data
- **Function**: `get_orderbook(symbol, limit=10)`

### 22. Get Funding Rate
- **Endpoint**: `/openApi/quote/v1/ticker/fundingRate`
- **Method**: `GET`
- **Authentication**: Not Required
- **Description**: Get funding rate
- **Function**: `get_funding_rate(symbol)`

### 23. Get Contracts Info
- **Endpoint**: `/openApi/swap/v2/quote/contracts`
- **Method**: `GET`
- **Authentication**: Not Required
- **Description**: Get contract information
- **Function**: `get_contracts_info()`

## Advanced Trading Endpoints

### 24. Get Force Orders
- **Endpoint**: `/openApi/swap/v2/trade/forceOrders`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get forced orders (liquidations, etc.)
- **Function**: `get_force_orders(symbol=None, auto_close_type=None, start_time=None, end_time=None, limit=50)`

### 25. Get Maintenance Margin Ratio
- **Endpoint**: `/openApi/swap/v1/maintMarginRatio`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get maintenance margin ratio
- **Function**: `get_maintenance_margin_ratio(symbol)`

### 26. Set Position Side Dual
- **Endpoint**: `/openApi/swap/v1/positionSide/dual`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Set dual position mode (hedge/one-way)
- **Function**: `set_position_side_dual(dual_side_position)`

### 27. Adjust Position Margin
- **Endpoint**: `/openApi/swap/v2/trade/positionMargin`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Add/remove margin from position
- **Function**: `adjust_position_margin(symbol, amount, type_margin)`

### 28. Set Auto Add Margin
- **Endpoint**: `/openApi/swap/v1/trade/autoAddMargin`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Enable/disable auto add margin
- **Function**: `set_auto_add_margin(symbol, auto_add_margin)`

### 29. Set Multi Assets Mode
- **Endpoint**: `/openApi/swap/v1/trade/assetMode`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Set multi-assets mode
- **Function**: `set_multi_assets_mode(multi_assets_margin)`

### 30. Get Multi Assets Rules
- **Endpoint**: `/openApi/swap/v1/trade/multiAssetsRules`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get multi-assets rules
- **Function**: `get_multi_assets_rules()`

### 31. Get Margin Assets
- **Endpoint**: `/openApi/swap/v1/user/marginAssets`
- **Method**: `GET`
- **Authentication**: Required
- **Description**: Get available margin assets
- **Function**: `get_margin_assets()`

### 32. Cancel All After
- **Endpoint**: `/openApi/swap/v2/trade/cancelAllAfter`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Cancel all orders after delay
- **Function**: `cancel_all_after(delay_num)`

### 33. Amend Order
- **Endpoint**: `/openApi/swap/v1/trade/amend`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Amend existing order
- **Function**: `amend_order(symbol, order_id, quantity=None, price=None)`

### 34. Reverse Position
- **Endpoint**: `/openApi/swap/v1/trade/reverse`
- **Method**: `POST`
- **Authentication**: Required
- **Description**: Reverse position
- **Function**: `reverse_position(symbol)`

## Error Handling

The API wrapper includes comprehensive error handling:
- HTTP status code validation
- API error code validation
- Network error handling
- JSON parsing error handling
- Demo mode with realistic mock data

## Demo Mode

All endpoints support demo mode with realistic mock data that maintains consistency across calls. To enable demo mode, initialize the API with `demo_mode=True`.

## WebSocket Integration

For real-time data, use the WebSocket endpoints:
- Market data: `wss://open-api-swap.bingx.com/swap-market`
- Account data: `wss://open-api-swap.bingx.com/swap-market?listenKey=...`