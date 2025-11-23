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
            response = requests.post(url, params=params, headers=headers)
        
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
        try:
            result = self._make_request('GET', '/openApi/swap/v2/user/balance', sign=True)
            return result.get('code') == 0
        except:
            return False
    
    def get_balance(self):
        """Получение баланса"""
        return self._make_request('GET', '/openApi/swap/v2/user/balance', sign=True)
    
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
    
    def place_order(self, symbol, side, quantity, order_type='LIMIT', price=None):
        """Размещение ордера"""
        if self.demo_mode:
            # В демо-режиме просто логируем
            return {"code": 0, "msg": "Order placed in demo mode", "data": {"orderId": "demo_order_123"}}
        
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        
        if price:
            params['price'] = price
        
        return self._make_request('POST', '/openApi/swap/v2/trade/order', params=params, sign=True)
    
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