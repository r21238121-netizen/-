"""
Updated BingX API Client based on the old project
This includes balance, PnL, positions, and other functionality from the old client
"""
import hmac
import hashlib
import time
import aiohttp
from urllib.parse import urlencode
from typing import Dict, Optional, Any
import logging

from config import config
from bingx_endpoints import ALL_ENDPOINTS


class BingXClient:
    def __init__(self, mode: str = "swap"):
        """
        Initialize BingX API client
        
        Args:
            mode: Trading mode - "swap" for futures or "spot" for spot trading
        """
        # Load API credentials directly from config
        self.api_key = config.API_KEY
        self.secret = config.SECRET_KEY
        
        # Validate that API keys are not None, empty, or using default placeholder values
        if not self.api_key or self.api_key in [None, '', 'YOUR_API_KEY_HERE']:
            raise ValueError("❌ BINGX_API_KEY is not set in config.py or is using default placeholder value. Please update config.py with your actual API key.")
        if not self.secret or self.secret in [None, '', 'YOUR_SECRET_HERE']:
            raise ValueError("❌ BINGX_SECRET is not set in config.py or is using default placeholder value. Please update config.py with your actual secret key.")
        
        # Use mode from config if not explicitly provided
        if mode == "swap" and hasattr(config, 'MODE'):
            self.mode = config.MODE
        else:
            self.mode = mode
            
        self.base_url = config.get_base_url()
        self.session = aiohttp.ClientSession()
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ BingX Client initialized successfully with valid API credentials")

    def _get_corrected_base_endpoint(self, endpoint: str) -> str:
        """
        Correct common endpoint issues based on API changes
        """
        # Some endpoints might have changed - try common alternatives
        if "quote/ticker/price" in endpoint:
            # Try alternative ticker endpoints
            alternatives = [
                endpoint.replace("quote/ticker/price", "market/ticker"),
                endpoint.replace("quote/ticker/price", "ticker/price"),
                endpoint
            ]
            for alt in alternatives:
                if self._test_endpoint(alt):
                    return alt
        elif "position/list" in endpoint:
            # Try alternative position endpoints
            alternatives = [
                endpoint.replace("position/list", "position"),
                endpoint.replace("position/list", "positions"),
                endpoint
            ]
            for alt in alternatives:
                if self._test_endpoint(alt):
                    return alt
        return endpoint

    def _test_endpoint(self, endpoint: str) -> bool:
        """
        Test if an endpoint is valid (helper method)
        """
        # This is just a placeholder - in practice, you'd need to actually test
        return True

    def _sign(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC-SHA256 signature for request authentication
        
        Args:
            params: Request parameters to sign
            
        Returns:
            Generated signature as hexadecimal string
        """
        query_string = urlencode(sorted(params.items()))
        signature = hmac.new(
            self.secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def get_balance(self) -> Dict[str, Any]:
        """
        Get account balance information
        
        Returns:
            Account balance data
        """
        if self.mode == "swap":
            endpoint = ALL_ENDPOINTS['get_balance']
        else:
            endpoint = "/openApi/spot/v1/account/balances"
        
        params = {"timestamp": int(time.time() * 1000)}
        params["signature"] = self._sign(params)

        headers = {"X-BX-APIKEY": self.api_key}
        try:
            async with self.session.get(f"{self.base_url}{endpoint}", headers=headers, params=params) as resp:
                result = await resp.json()
                self.logger.info(f"Balance retrieved: {result}")
                return result
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            raise

    async def place_order(self, symbol: str, side: str, quantity: str, price: Optional[str] = None, 
                         leverage: int = 1, order_type: str = "MARKET") -> Dict[str, Any]:
        """
        Place a new order
        
        Args:
            symbol: Trading pair (e.g., "BTC-USDT")
            side: Order side ("BUY" or "SELL")
            quantity: Order quantity
            price: Order price (for limit orders)
            leverage: Leverage for futures trading
            order_type: Order type ("MARKET", "LIMIT", etc.)
            
        Returns:
            Order placement result
        """
        if self.mode == "swap":
            endpoint = ALL_ENDPOINTS['place_order']
            params = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "positionSide": "BOTH",
                "quantity": quantity,
                "leverage": leverage,
                "timestamp": int(time.time() * 1000)
            }
            if price and order_type == "LIMIT":
                params["price"] = price
        else:
            endpoint = "/openApi/spot/v1/trade/order"
            params = {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                "timestamp": int(time.time() * 1000)
            }
            if price and order_type == "LIMIT":
                params["price"] = price
        
        params["signature"] = self._sign(params)

        headers = {"X-BX-APIKEY": self.api_key}
        try:
            async with self.session.post(f"{self.base_url}{endpoint}", headers=headers, params=params) as resp:
                result = await resp.json()
                self.logger.info(f"Order placed: {result}")
                return result
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            raise

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Get ticker price for a specific symbol
        
        Args:
            symbol: Trading pair (e.g., "BTC-USDT")
            
        Returns:
            Ticker price data
        """
        # Try multiple endpoint variations as the API might have changed
        endpoints_to_try = [
            f"/openApi/swap/v2/quote/ticker/price?symbol={symbol}",
            f"/openApi/swap/v1/quote/ticker/price?symbol={symbol}",
            f"/openApi/market/ticker/price?symbol={symbol}",
            f"/openApi/ticker/price?symbol={symbol}"
        ]
        
        params = {"symbol": symbol} if symbol else {}
        
        for endpoint in endpoints_to_try:
            try:
                # Extract the actual endpoint path without query parameters for proper formatting
                if '?' in endpoint:
                    path, query_part = endpoint.split('?', 1)
                    query_params = dict(param.split('=') for param in query_part.split('&'))
                    # Merge with symbol param
                    query_params.update(params)
                else:
                    path = endpoint
                    query_params = params if params else {}
                
                async with self.session.get(f"{self.base_url}{path}", params=query_params) as resp:
                    result = await resp.json()
                    if result.get("code") == 0 or (result.get("code") != 100400 and "not exist" not in result.get("msg", "")):
                        self.logger.info(f"Ticker retrieved for {symbol}: {result}")
                        return result
            except Exception as e:
                self.logger.error(f"Error trying ticker endpoint {endpoint}: {e}")
                continue
        
        # If all endpoints fail, return an error response
        self.logger.error(f"Unable to retrieve ticker for {symbol} - all endpoints failed")
        return {
            "code": 100400,
            "msg": "Unable to retrieve ticker - all endpoints failed",
            "data": {}
        }

    async def get_positions(self) -> Optional[Dict[str, Any]]:
        """
        Get current positions (only available in swap mode)
        
        Returns:
            Position data or None if in spot mode
        """
        if self.mode == "swap":
            endpoint = ALL_ENDPOINTS['get_positions']
            
            params = {"timestamp": int(time.time() * 1000)}
            params["signature"] = self._sign(params)

            headers = {"X-BX-APIKEY": self.api_key}
            
            try:
                async with self.session.get(f"{self.base_url}{endpoint}", headers=headers, params=params) as resp:
                    result = await resp.json()
                    if result.get("code") == 0:
                        self.logger.info(f"Positions retrieved: {result}")
                        return result
                    else:
                        self.logger.error(f"Error retrieving positions: {result}")
                        return result
            except Exception as e:
                self.logger.error(f"Error getting positions: {e}")
                # Return an error response that matches expected format
                return {
                    "code": 100400,
                    "msg": f"Unable to retrieve positions: {str(e)}",
                    "data": []
                }
        else:
            self.logger.warning("Positions not available in spot mode")
            print("❌ В споте нет позиций")
            return None

    async def get_pnl(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get profit and loss for a specific symbol by retrieving position information
        
        Args:
            symbol: Trading pair to check PnL for
            
        Returns:
            PnL data for the symbol
        """
        if self.mode == "swap":
            # Get positions to find PnL information
            positions_data = await self.get_positions()
            if positions_data and positions_data.get("data"):
                # Filter positions for the specific symbol
                symbol_positions = [pos for pos in positions_data["data"] if pos.get("symbol") == symbol]
                return {
                    "code": 0,
                    "msg": "",
                    "data": symbol_positions
                }
            return positions_data
        else:
            self.logger.warning("PnL not available in spot mode")
            print("❌ PnL недоступна в споте")
            return None

    async def get_all_pnl(self) -> Optional[Dict[str, Any]]:
        """
        Get profit and loss for all positions by retrieving all positions
        
        Returns:
            PnL data for all positions
        """
        if self.mode == "swap":
            return await self.get_positions()
        else:
            self.logger.warning("PnL not available in spot mode")
            print("❌ PnL недоступна в споте")
            return None

    async def close_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Close position for a specific symbol (only available in swap mode)
        
        Args:
            symbol: Trading pair to close position for
            
        Returns:
            Close position result or None if in spot mode
        """
        if self.mode == "swap":
            # First get the current position to determine side and size to close
            positions_data = await self.get_positions()
            if positions_data and positions_data.get("data"):
                # Find the position for the given symbol
                target_position = None
                for pos in positions_data["data"]:
                    if pos.get("symbol") == symbol:
                        # Check if there's an actual position (not just zero position)
                        if float(pos.get("positionAmt", 0)) != 0:
                            target_position = pos
                            break
                
                if target_position:
                    # Place an order in the opposite direction to close the position
                    side = "SELL" if target_position.get("positionSide") == "LONG" or float(target_position.get("positionAmt", 0)) > 0 else "BUY"
                    quantity = str(abs(float(target_position.get("positionAmt", 0))))
                    
                    # Place market order to close position
                    close_order = await self.place_order(
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        order_type="MARKET"
                    )
                    return close_order
                else:
                    # No position found to close
                    return {
                        "code": 0,
                        "msg": "No position found to close",
                        "data": {}
                    }
            else:
                return {
                    "code": 0,
                    "msg": "No positions found",
                    "data": {}
                }
        else:
            self.logger.warning("Closing position not available in spot mode")
            print("❌ В споте нельзя закрыть позицию как в фьючерсах")
            return None

    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get comprehensive account information
        
        Returns:
            Complete account information including balance and positions
        """
        try:
            balance = await self.get_balance()
            positions = await self.get_positions() if self.mode == "swap" else None
            
            account_info = {
                "balance": balance,
                "positions": positions,
                "mode": self.mode
            }
            
            self.logger.info("Account info retrieved successfully")
            return account_info
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            raise

    async def get_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get currently open orders
        
        Args:
            symbol: Trading pair (optional filter)
            
        Returns:
            List of open orders
        """
        if self.mode == "swap":
            endpoint = ALL_ENDPOINTS['get_open_orders']
        else:
            endpoint = "/openApi/spot/v1/trade/openOrders"
            
        params = {"timestamp": int(time.time() * 1000)}
        if symbol:
            params["symbol"] = symbol
        params["signature"] = self._sign(params)

        headers = {"X-BX-APIKEY": self.api_key}
        try:
            async with self.session.get(f"{self.base_url}{endpoint}", headers=headers, params=params) as resp:
                result = await resp.json()
                self.logger.info(f"Open orders retrieved: {result}")
                return result
        except Exception as e:
            self.logger.error(f"Error getting open orders: {e}")
            raise

    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """
        Cancel an existing order
        
        Args:
            symbol: Trading pair
            order_id: Order ID to cancel
            
        Returns:
            Cancellation result
        """
        if self.mode == "swap":
            endpoint = ALL_ENDPOINTS['cancel_order']
            params = {
                "symbol": symbol,
                "orderId": order_id,
                "timestamp": int(time.time() * 1000)
            }
            params["signature"] = self._sign(params)
        else:
            endpoint = "/openApi/spot/v1/trade/cancel"
            params = {
                "symbol": symbol,
                "orderId": order_id,
                "timestamp": int(time.time() * 1000)
            }
            params["signature"] = self._sign(params)

        headers = {"X-BX-APIKEY": self.api_key}
        try:
            # Note: According to user data, cancel_order uses DELETE method
            async with self.session.delete(f"{self.base_url}{endpoint}", headers=headers, params=params) as resp:
                result = await resp.json()
                self.logger.info(f"Order {order_id} cancelled: {result}")
                return result
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            raise

    async def get_klines(self, symbol: str, interval: str = "1m", limit: int = 100) -> Dict[str, Any]:
        """
        Get candlestick/kline data
        
        Args:
            symbol: Trading pair
            interval: Candlestick interval ("1m", "5m", "1h", etc.)
            limit: Number of candles to return (max 1000)
            
        Returns:
            Kline/candlestick data
        """
        endpoint = ALL_ENDPOINTS['get_kline_data']
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        try:
            async with self.session.get(f"{self.base_url}{endpoint}", params=params) as resp:
                result = await resp.json()
                self.logger.info(f"Klines retrieved for {symbol}: {len(result.get('data', []))} candles")
                return result
        except Exception as e:
            self.logger.error(f"Error getting klines: {e}")
            raise

    async def get_orderbook(self, symbol: str) -> Dict[str, Any]:
        """
        Get order book depth for a symbol
        
        Args:
            symbol: Trading pair
            
        Returns:
            Order book depth data
        """
        endpoint = ALL_ENDPOINTS['get_orderbook']
        params = {"symbol": symbol}
        try:
            async with self.session.get(f"{self.base_url}{endpoint}", params=params) as resp:
                result = await resp.json()
                self.logger.info(f"Orderbook retrieved for {symbol}")
                return result
        except Exception as e:
            self.logger.error(f"Error getting orderbook: {e}")
            raise

    async def close(self):
        """
        Close the aiohttp session
        """
        await self.session.close()
        self.logger.info("BingX client session closed")


# Example usage function
async def main():
    """
    Example usage of the updated BingX client
    """
    print("=== Updated BingX API Client ===\n")
    
    # Initialize API client
    client = BingXClient(mode="swap")  # Use "spot" for spot trading
    
    try:
        print("1. Getting account balance...")
        balance = await client.get_balance()
        print(f"Balance: {balance}\n")

        print("2. Getting BTC-USDT ticker...")
        ticker = await client.get_ticker("BTC-USDT")
        print(f"BTC-USDT Price: {ticker}\n")

        print("3. Getting current positions...")
        positions = await client.get_positions()
        print(f"Positions: {positions}\n")

        print("4. Getting PnL for BTC-USDT...")
        pnl = await client.get_pnl("BTC-USDT")
        print(f"PnL: {pnl}\n")

        print("5. Getting K-lines for BTC-USDT...")
        klines = await client.get_klines("BTC-USDT", "1m", 5)
        if klines.get("data"):
            latest_candle = klines["data"][-1]
            print(f"Latest candle: {latest_candle}\n")

        print("6. Getting open orders...")
        orders = await client.get_open_orders()
        print(f"Open orders: {orders}\n")

    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the session
        await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())