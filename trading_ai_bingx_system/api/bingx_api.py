import hashlib
import hmac
import time
import requests
from urllib.parse import urlencode
import json
from config.config import BINGX_API_KEY, BINGX_SECRET_KEY, BINGX_BASE_URL

class BingXAPI:
    def __init__(self):
        self.api_key = BINGX_API_KEY
        self.secret_key = BINGX_SECRET_KEY
        self.base_url = BINGX_BASE_URL

    def _generate_signature(self, payload):
        """Генерация подписи для запроса к API"""
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _get_headers(self):
        """Получение заголовков для запроса"""
        return {
            'X-BX-APIKEY': self.api_key
        }

    def get_server_time(self):
        """Получение времени сервера"""
        endpoint = "/openApi/v1/time"
        url = self.base_url + endpoint
        response = requests.get(url)
        return response.json()

    def get_futures_symbols(self):
        """Получение списка фьючерсных пар"""
        endpoint = "/openApi/quote/v1/ticker/24hr"
        url = self.base_url + endpoint
        response = requests.get(url)
        return response.json()

    def get_kline_data(self, symbol, interval, limit=500):
        """Получение исторических данных (свечи)"""
        endpoint = "/openApi/quote/v1/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        url = self.base_url + endpoint + "?" + urlencode(params)
        response = requests.get(url)
        return response.json()

    def get_account_info(self):
        """Получение информации о счете"""
        endpoint = "/openApi/swap/v1/account/list"
        timestamp = int(time.time() * 1000)
        
        # Подготовка параметров
        params = {
            'timestamp': timestamp
        }
        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params['signature'] = signature
        
        url = self.base_url + endpoint + "?" + urlencode(params)
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        return response.json()

    def get_position_info(self):
        """Получение информации о позициях"""
        endpoint = "/openApi/swap/v1/position/list"
        timestamp = int(time.time() * 1000)
        
        params = {
            'timestamp': timestamp
        }
        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params['signature'] = signature
        
        url = self.base_url + endpoint + "?" + urlencode(params)
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        return response.json()

    def place_order(self, symbol, side, position_side, order_type, quantity, price=None, stop_loss=None, take_profit=None):
        """Размещение ордера"""
        endpoint = "/openApi/swap/v1/trade/order"
        timestamp = int(time.time() * 1000)
        
        params = {
            'symbol': symbol,
            'side': side,  # BUY или SELL
            'positionSide': position_side,  # LONG или SHORT
            'type': order_type,  # LIMIT, MARKET и т.д.
            'quantity': quantity,
            'timestamp': timestamp
        }
        
        if price:
            params['price'] = price
        if stop_loss:
            params['stopLoss'] = stop_loss
        if take_profit:
            params['takeProfit'] = take_profit
            
        query_string = urlencode(sorted(params.items()))
        signature = self._generate_signature(query_string)
        params['signature'] = signature
        
        url = self.base_url + endpoint
        headers = self._get_headers()
        
        response = requests.post(url, headers=headers, params=params)
        return response.json()

    def cancel_order(self, symbol, order_id):
        """Отмена ордера"""
        endpoint = "/openApi/swap/v1/trade/order"
        timestamp = int(time.time() * 1000)
        
        params = {
            'symbol': symbol,
            'orderId': order_id,
            'timestamp': timestamp
        }
        
        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params['signature'] = signature
        
        url = self.base_url + endpoint
        headers = self._get_headers()
        
        response = requests.delete(url, headers=headers, params=params)
        return response.json()

    def get_open_orders(self, symbol=None):
        """Получение активных ордеров"""
        endpoint = "/openApi/swap/v1/trade/openOrders"
        timestamp = int(time.time() * 1000)
        
        params = {
            'timestamp': timestamp
        }
        if symbol:
            params['symbol'] = symbol
            
        query_string = urlencode(params)
        signature = self._generate_signature(query_string)
        params['signature'] = signature
        
        url = self.base_url + endpoint + "?" + urlencode(params)
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        return response.json()

# Пример использования
if __name__ == "__main__":
    api = BingXAPI()
    
    # Получение времени сервера
    server_time = api.get_server_time()
    print("Server time:", server_time)
    
    # Получение информации о счете
    # account_info = api.get_account_info()
    # print("Account info:", account_info)