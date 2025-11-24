"""
Модуль взаимодействия с API BingX
"""
import requests
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode


class BingXAPI:
    def __init__(self, api_key=None, secret_key=None, demo_mode=False):
        self.api_key = api_key
        self.secret_key = secret_key
        self.demo_mode = demo_mode
        
        if demo_mode:
            self.base_url = "https://open-api.bingx.com"
            self.websocket_url = "wss://open-api-ws.bingx.com"
        else:
            self.base_url = "https://open-api.bingx.com"
            self.websocket_url = "wss://open-api-ws.bingx.com"
    
    def _generate_signature(self, params_str):
        """Генерация подписи для запроса"""
        if not self.secret_key:
            raise ValueError("Secret key is required for signing requests")
        
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            params_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, method, endpoint, params=None, sign=False):
        """Выполнение HTTP-запроса к API"""
        if self.demo_mode:
            # В демо-режиме возвращаем фиктивные данные
            return self._get_demo_data(endpoint)
        
        url = f"{self.base_url}{endpoint}"
        
        if sign:
            params = params or {}
            params['timestamp'] = str(int(time.time() * 1000))
            query_string = urlencode(params)
            signature = self._generate_signature(query_string)
            params['signature'] = signature
        
        headers = {
            'X-BX-APIKEY': self.api_key
        }
        
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, data=params, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, params=params, headers=headers)
        
        return response.json()
    
    def _get_demo_data(self, endpoint):
        """Получение демо-данных"""
        # Возвращаем фиктивные данные для демо-режима
        if '/user/balance' in endpoint:
            return {
                "code": 0,
                "msg": "",
                "data": {
                    "balances": [
                        {
                            "asset": "USDT",
                            "walletBalance": "10000.00",
                            "unrealizedProfit": "0.00",
                            "marginBalance": "10000.00"
                        }
                    ]
                }
            }
        elif '/user/positions' in endpoint:
            return {
                "code": 0,
                "msg": "",
                "data": [
                    {
                        "symbol": "BTC-USDT",
                        "positionAmt": "0.001",
                        "entryPrice": "60000.00",
                        "unrealizedProfit": "50.00",
                        "leverage": "10",
                        "positionSide": "LONG"
                    }
                ]
            }
        elif '/user/income' in endpoint:
            return {
                "code": 0,
                "msg": "",
                "data": [
                    {
                        "symbol": "BTC-USDT",
                        "incomeType": "REALIZED_PNL",
                        "income": "25.50",
                        "asset": "USDT",
                        "time": int(time.time() * 1000),
                        "info": "Realized PnL for closed position"
                    },
                    {
                        "symbol": "ETH-USDT",
                        "incomeType": "FUNDING_FEE",
                        "income": "-1.20",
                        "asset": "USDT",
                        "time": int(time.time() * 1000) - 3600000,  # 1 hour ago
                        "info": "Funding fee"
                    }
                ]
            }
        elif '/user/commissionRate' in endpoint:
            return {
                "code": 0,
                "msg": "",
                "data": {
                    "symbol": "BTC-USDT",
                    "maker": "0.0002",
                    "taker": "0.0005"
                }
            }
        elif '/trade/myTrades' in endpoint:
            return {
                "code": 0,
                "msg": "",
                "data": [
                    {
                        "symbol": "BTC-USDT",
                        "id": "123456",
                        "orderId": "789012",
                        "side": "BUY",
                        "price": "60000.00",
                        "qty": "0.001",
                        "realizedPnl": "50.00",
                        "fee": "-0.0005",
                        "time": int(time.time() * 1000)
                    }
                ]
            }
        elif '/ticker/price' in endpoint:
            return {
                "code": 0,
                "msg": "",
                "data": [
                    {
                        "symbol": "BTC-USDT",
                        "price": "60000.00"
                    }
                ]
            }
        else:
            return {"code": 0, "msg": "", "data": {}}
    
    def validate_credentials(self):
        """Проверка валидности API-ключей"""
        if self.demo_mode:
            # В демо-режиме всегда возвращаем True
            return True
        
        try:
            result = self._make_request('GET', '/openApi/swap/v3/user/balance', sign=True)
            return result.get('code') == 0
        except Exception as e:
            # Логируем ошибку для отладки, но возвращаем False
            print(f"Ошибка при проверке валидности API-ключей: {e}")
            return False
    
    # Управление ордерами
    def place_order(self, symbol, side, quantity, order_type='LIMIT', price=None, position_side='BOTH'):
        """Создать ордер (limit/market)"""
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'positionSide': position_side
        }
        
        if price:
            params['price'] = price
        
        return self._make_request('POST', '/openApi/swap/v2/trade/order', params=params, sign=True)
    
    def place_batch_orders(self, orders):
        """Массовое создание ордеров"""
        params = {
            'orders': orders
        }
        return self._make_request('POST', '/openApi/swap/v2/trade/batchOrders', params=params, sign=True)
    
    def cancel_order(self, symbol, order_id):
        """Отменить ордер"""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('DELETE', '/openApi/swap/v2/trade/order', params=params, sign=True)
    
    def cancel_all_open_orders(self, symbol):
        """Отменить все открытые ордера"""
        params = {
            'symbol': symbol
        }
        return self._make_request('DELETE', '/openApi/swap/v2/trade/allOpenOrders', params=params, sign=True)
    
    def get_open_orders(self, symbol=None):
        """Список открытых ордеров"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._make_request('GET', '/openApi/swap/v2/trade/openOrders', params=params, sign=True)
    
    def get_all_orders(self, symbol, start_time=None, end_time=None, limit=500):
        """История всех ордеров"""
        params = {
            'symbol': symbol,
            'limit': limit
        }
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        return self._make_request('GET', '/openApi/swap/v2/trade/allOrders', params=params, sign=True)
    
    # Позиции
    def get_positions(self, symbol=None):
        """Список открытых позиций"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._make_request('GET', '/openApi/swap/v2/user/positions', params=params, sign=True)
    
    def close_position(self, symbol, position_side='BOTH'):
        """Закрыть позицию рыночным ордером"""
        params = {
            'symbol': symbol,
            'positionSide': position_side
        }
        return self._make_request('POST', '/openApi/swap/v2/position/closePosition', params=params, sign=True)
    
    def set_margin_mode(self, symbol, margin_mode):
        """Установить режим маржи (cross/isolated)"""
        params = {
            'symbol': symbol,
            'marginMode': margin_mode
        }
        return self._make_request('POST', '/openApi/swap/v2/position/setMarginMode', params=params, sign=True)
    
    def set_leverage(self, symbol, leverage, position_side='BOTH'):
        """Установить плечо"""
        params = {
            'symbol': symbol,
            'leverage': leverage,
            'positionSide': position_side
        }
        return self._make_request('POST', '/openApi/swap/v2/position/setLeverage', params=params, sign=True)
    
    def set_tp_sl(self, symbol, take_profit=None, stop_loss=None, position_side='BOTH'):
        """Установить Take Profit / Stop Loss"""
        params = {
            'symbol': symbol,
            'positionSide': position_side
        }
        if take_profit:
            params['takeProfit'] = take_profit
        if stop_loss:
            params['stopLoss'] = stop_loss
        return self._make_request('POST', '/openApi/swap/v2/position/setTPSL', params=params, sign=True)
    
    # Баланс и счёт
    def get_balance(self):
        """Получить баланс аккаунта"""
        return self._make_request('GET', '/openApi/swap/v3/user/balance', sign=True)
    
    def get_account_info(self):
        """Информация о счёте (режим маржи, плечо и т.д.)"""
        return self._make_request('GET', '/openApi/swap/v2/user/account', sign=True)
    
    def get_income_history(self, symbol=None, income_type=None, start_time=None, end_time=None, limit=1000):
        """История прибыли/убытков (PnL, комиссии, финансирование и т.д.)"""
        params = {'limit': limit}
        if symbol:
            params['symbol'] = symbol
        if income_type:
            params['incomeType'] = income_type
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        return self._make_request('GET', '/openApi/swap/v2/user/income', params=params, sign=True)
    
    def get_commission_rate(self, symbol):
        """Текущие комиссии для символа"""
        params = {'symbol': symbol}
        return self._make_request('GET', '/openApi/swap/v2/user/commissionRate', params=params, sign=True)
    
    # История сделок
    def get_my_trades(self, symbol, limit=500):
        """История сделок"""
        params = {
            'symbol': symbol,
            'limit': limit
        }
        return self._make_request('GET', '/openApi/swap/v2/trade/myTrades', params=params, sign=True)
    
    # Дополнительные методы
    def get_market_price(self, symbol):
        """Получение текущей цены"""
        params = {'symbol': symbol}
        return self._make_request('GET', '/openApi/swap/v1/ticker/price', params=params)
    
    def get_kline_data(self, symbol, interval='1h', limit=100):
        """Получение исторических данных (свечи)"""
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        return self._make_request('GET', '/openApi/swap/v1/depthKlines', params=params)
    
    def get_open_interest(self, symbol):
        """Получение Open Interest"""
        params = {'symbol': symbol}
        return self._make_request('GET', '/openApi/quote/v1/depthKlines/openInterest', params=params)
    
    def get_funding_rate(self, symbol):
        """Получение Funding Rate"""
        params = {'symbol': symbol}
        return self._make_request('GET', '/openApi/quote/v1/ticker/fundingRate', params=params)
    
    def get_orderbook(self, symbol, limit=10):
        """Получение стакана ордеров"""
        params = {'symbol': symbol, 'limit': limit}
        return self._make_request('GET', '/openApi/swap/v1/depth', params=params)