"""
Example usage of the BingX API client
Demonstrates various API functionalities
"""

from bingx_api import BingXAPI
from config import config
import json


def main():
    """
    Comprehensive example of using the BingX API client
    """
    print("=== BingX API Professional Client ===\n")
    
    # Get API credentials from config
    credentials = config.get_api_credentials()
    api_key = credentials['api_key']
    secret_key = credentials['secret_key']
    base_url = config.get_base_url()

    # Initialize API client
    api = BingXAPI(api_key=api_key, secret_key=secret_key, base_url=base_url)
    
    print(f"Demo mode: {config.is_demo_mode()}")
    print(f"Base URL: {base_url}\n")

    try:
        print("1. Testing public market data endpoints...\n")
        
        # Example 1: Get market data (unsigned request)
        print("Getting BTC-USDT klines (1m interval, 5 candles)...")
        klines = api.get_klines(symbol="BTC-USDT", interval="1m", limit=5)
        if klines.get("data") and len(klines["data"]) > 0:
            latest_candle = klines["data"][-1]
            print(f"Latest candle: {latest_candle}")
        else:
            print("No kline data returned")
        print()

        # Example 2: Get ticker information
        print("Getting BTC-USDT ticker...")
        ticker = api.get_ticker(symbol="BTC-USDT")
        print(f"Ticker: {json.dumps(ticker, indent=2)}")
        print()

        # Example 3: Get order book depth
        print("Getting BTC-USDT order book depth...")
        depth = api.get_depth("BTC-USDT")
        print(f"Depth: {json.dumps(depth, indent=2)[:200]}...")  # Truncate output
        print()

        print("2. Testing authenticated endpoints (will fail with demo keys)...\n")
        
        # Example 4: Get account balance (signed request)
        # Note: This will likely fail with demo keys but demonstrates the method
        print("Attempting to get account balance...")
        try:
            balance = api.get_balance()
            print(f"Balance: {json.dumps(balance, indent=2)}")
        except Exception as e:
            print(f"Expected error with demo keys: {e}")
        print()

        # Example 5: Get open orders
        print("Attempting to get open orders...")
        try:
            orders = api.get_open_orders()
            print(f"Open orders: {json.dumps(orders, indent=2)}")
        except Exception as e:
            print(f"Expected error with demo keys: {e}")
        print()

        # Example 6: WebSocket listen key (for private streams)
        print("Attempting to create listen key...")
        try:
            listen_key_data = api.create_listen_key()
            print(f"Listen key: {json.dumps(listen_key_data, indent=2)}")
        except Exception as e:
            print(f"Expected error with demo keys: {e}")
        print()

        print("3. Testing order operations (simulation)...\n")
        
        # Example 7: Place a market order (simulation)
        # Note: This is commented out to prevent actual trading with simulation keys
        print("Order placement would work like this (not executed with demo keys):")
        print("# order_response = api.place_order(")
        print("#     symbol=\"BTC-USDT\",")
        print("#     side=\"BUY\",")
        print("#     order_type=\"MARKET\",")
        print("#     quantity=\"0.001\",")
        print("#     position_side=\"LONG\"")
        print("# )")
        print()

        print("=== All examples completed successfully ===")
        print("Note: Authenticated endpoints failed as expected with demo keys")
        print("Replace with real API keys to use authenticated endpoints")

    except Exception as e:
        print(f"Error occurred during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()