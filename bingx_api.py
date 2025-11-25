"""
Professional BingX API Implementation
Production-level secure implementation with proper error handling
"""

import time
import hmac
import hashlib
import requests
from typing import Dict, Optional, Any
import logging
from config import config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BingXAPI:
    """
    Professional BingX API Client
    Implements secure communication with BingX exchange using HMAC-SHA256 signatures
    """
    
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://open-api.bingx.com"):
        """
        Initialize BingX API client
        
        Args:
            api_key: Your BingX API key
            secret_key: Your BingX secret key
            base_url: BingX API base URL (default for production)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip('/')
        
        # Create session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            "X-BX-APIKEY": self.api_key,
            "Content-Type": "application/json"
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.rate_limit_delay = config.RATE_LIMIT_DELAY  # seconds
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _enforce_rate_limit(self):
        """Enforce rate limiting to prevent exceeding API limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def _generate_signature(self, query_string: str) -> str:
        """
        Generate HMAC-SHA256 signature for request authentication
        
        Args:
            query_string: URL-encoded parameters string
            
        Returns:
            Generated signature as hexadecimal string
        """
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _create_signed_request(self, method: str, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create and send a signed API request
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            path: API endpoint path
            params: Request parameters (optional)
            
        Returns:
            API response as dictionary
        """
        self._enforce_rate_limit()
        
        if params is None:
            params = {}
        
        # Add timestamp to parameters
        params["timestamp"] = str(int(time.time() * 1000))
        
        # Sort parameters lexicographically
        sorted_params = sorted(params.items())
        query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
        
        # Generate signature
        signature = self._generate_signature(query_string)
        
        # Complete URL with parameters and signature
        url = f"{self.base_url}{path}?{query_string}&signature={signature}"
        
        try:
            response = self.session.request(method, url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Handle empty response body (like from PUT requests)
            if response.content:
                return response.json()
            else:
                # Return a success response if no content is expected
                return {"code": 0, "msg": "success", "data": {}}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response: {e.response.text}")
                self.logger.error(f"Status Code: {e.response.status_code}")
            raise
        except ValueError as e:  # JSON decode error
            self.logger.error(f"Failed to decode JSON response: {e}")
            # If we get here, it means the response was not JSON but maybe we can still work with it
            if hasattr(e, 'response') and e.response is not None:
                # Return the text response as data
                return {"code": 0, "msg": "success", "data": {"raw_response": e.response.text}}
            raise

    def _create_unsigned_request(self, method: str, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create and send an unsigned public API request
        
        Args:
            method: HTTP method
            path: API endpoint path
            params: Request parameters (optional)
            
        Returns:
            API response as dictionary
        """
        self._enforce_rate_limit()
        
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, params=params, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Handle empty response body
            if response.content:
                return response.json()
            else:
                # Return a success response if no content is expected
                return {"code": 0, "msg": "success", "data": {}}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Public API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response: {e.response.text}")
                self.logger.error(f"Status Code: {e.response.status_code}")
            raise
        except ValueError as e:  # JSON decode error
            self.logger.error(f"Failed to decode JSON response: {e}")
            # If we get here, it means the response was not JSON but maybe we can still work with it
            if hasattr(e, 'response') and e.response is not None:
                # Return the text response as data
                return {"code": 0, "msg": "success", "data": {"raw_response": e.response.text}}
            raise

    # Account and Trading Endpoints
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance information
        
        Returns:
            Account balance data
        """
        path = "/openApi/swap/v3/user/balance"
        return self._create_signed_request("GET", path)

    def place_order(self, symbol: str, side: str, order_type: str, quantity: str, position_side: str = "LONG") -> Dict[str, Any]:
        """
        Place a new order
        
        Args:
            symbol: Trading pair (e.g., "BTC-USDT")
            side: Order side ("BUY" or "SELL")
            order_type: Order type ("MARKET", "LIMIT", etc.)
            quantity: Order quantity
            position_side: Position side ("LONG" or "SHORT") for futures
            
        Returns:
            Order placement result
        """
        path = "/openApi/swap/v2/trade/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "positionSide": position_side
        }
        return self._create_signed_request("POST", path, params)

    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        Cancel an existing order
        
        Args:
            symbol: Trading pair
            order_id: Order ID to cancel
            
        Returns:
            Cancellation result
        """
        path = "/openApi/swap/v2/trade/cancel"
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        return self._create_signed_request("DELETE", path, params)

    def get_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get currently open orders
        
        Args:
            symbol: Trading pair (optional filter)
            
        Returns:
            List of open orders
        """
        path = "/openApi/swap/v2/trade/openOrders"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._create_signed_request("GET", path, params)

    def get_order_history(self, symbol: str, start_time: Optional[int] = None, end_time: Optional[int] = None) -> Dict[str, Any]:
        """
        Get order history
        
        Args:
            symbol: Trading pair
            start_time: Start time in milliseconds (optional)
            end_time: End time in milliseconds (optional)
            
        Returns:
            Order history
        """
        path = "/openApi/swap/v2/trade/allOrders"
        params = {"symbol": symbol}
        if start_time:
            params["startTime"] = str(start_time)
        if end_time:
            params["endTime"] = str(end_time)
        return self._create_signed_request("GET", path, params)

    # Market Data Endpoints (Public)
    
    def get_klines(self, symbol: str = "BTC-USDT", interval: str = "1m", limit: int = 100) -> Dict[str, Any]:
        """
        Get candlestick/kline data
        
        Args:
            symbol: Trading pair
            interval: Candlestick interval ("1m", "5m", "1h", etc.)
            limit: Number of candles to return (max 1000)
            
        Returns:
            Kline/candlestick data
        """
        path = "/openApi/swap/v2/quote/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        return self._create_unsigned_request("GET", path, params)

    def get_ticker(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get ticker price (last price) for symbol(s)
        
        Args:
            symbol: Trading pair (required for this endpoint)
            
        Returns:
            Ticker price data
        """
        path = "/openApi/swap/v2/quote/ticker/price"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._create_unsigned_request("GET", path, params)

    def get_24hr_ticker(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get 24hr ticker price change statistics
        
        Args:
            symbol: Trading pair (optional, returns all if not specified)
            
        Returns:
            24hr Ticker data
        """
        path = "/openApi/swap/v1/quote/ticker/24hr"
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._create_unsigned_request("GET", path, params)

    def get_depth(self, symbol: str) -> Dict[str, Any]:
        """
        Get order book depth
        
        Args:
            symbol: Trading pair
            
        Returns:
            Order book depth data
        """
        path = "/openApi/swap/v2/quote/depth"
        params = {"symbol": symbol}
        return self._create_unsigned_request("GET", path, params)

    def get_trades(self, symbol: str, limit: int = 500) -> Dict[str, Any]:
        """
        Get recent trades
        
        Args:
            symbol: Trading pair
            limit: Number of trades to return (max 1000)
            
        Returns:
            Recent trades data
        """
        path = "/openApi/swap/v2/quote/trades"
        params = {
            "symbol": symbol,
            "limit": limit
        }
        return self._create_unsigned_request("GET", path, params)

    # WebSocket Listen Key (for private streams)
    
    def create_listen_key(self) -> Dict[str, Any]:
        """
        Create a listen key for WebSocket private streams
        
        Returns:
            Listen key data
        """
        path = "/openApi/user/auth/userDataStream"
        return self._create_signed_request("POST", path)

    def extend_listen_key(self, listen_key: str) -> Dict[str, Any]:
        """
        Extend the validity of a listen key
        
        Args:
            listen_key: Existing listen key to extend
            
        Returns:
            Extension result
        """
        path = "/openApi/user/auth/userDataStream"
        params = {"listenKey": listen_key}
        return self._create_signed_request("PUT", path, params)

    def close_listen_key(self, listen_key: str) -> Dict[str, Any]:
        """
        Close a listen key
        
        Args:
            listen_key: Listen key to close
            
        Returns:
            Close result
        """
        path = "/openApi/user/auth/userDataStream"
        params = {"listenKey": listen_key}
        return self._create_signed_request("DELETE", path, params)


def main():
    """
    Example usage of the BingX API client
    """
    # Get API credentials from config
    credentials = config.get_api_credentials()
    api_key = credentials['api_key']
    secret_key = credentials['secret_key']
    base_url = config.get_base_url()

    # Initialize API client
    api = BingXAPI(api_key=api_key, secret_key=secret_key, base_url=base_url)

    try:
        # Example 1: Get account balance (signed request)
        print("Getting account balance...")
        balance = api.get_balance()
        print(f"Balance: {balance}")

        # Example 2: Get market data (unsigned request)
        print("\nGetting BTC-USDT klines...")
        klines = api.get_klines(symbol="BTC-USDT", interval="1m", limit=5)
        if klines.get("data") and len(klines["data"]) > 0:
            latest_candle = klines["data"][-1]
            print(f"Latest candle: {latest_candle}")

        # Example 3: Place a market order (simulation)
        # Note: This is commented out to prevent actual trading with simulation keys
        # order_response = api.place_order(
        #     symbol="BTC-USDT",
        #     side="BUY",
        #     order_type="MARKET",
        #     quantity="0.001",
        #     position_side="LONG"
        # )
        # print(f"Order placed: {order_response}")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()