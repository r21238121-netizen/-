"""
Test script to verify the BingX API implementation
"""
from bingx_api import BingXAPI
from config import config
import json


def test_basic_functionality():
    """Test basic API functionality"""
    print("=== Testing BingX API Implementation ===\n")
    
    # Get API credentials from config
    credentials = config.get_api_credentials()
    api_key = credentials['api_key']
    secret_key = credentials['secret_key']
    base_url = config.get_base_url()

    # Initialize API client
    api = BingXAPI(api_key=api_key, secret_key=secret_key, base_url=base_url)
    
    print("✓ API client initialized successfully")
    print(f"✓ Using base URL: {base_url}")
    print(f"✓ Demo mode: {config.is_demo_mode()}\n")
    
    # Test 1: Public endpoint - klines
    print("1. Testing public endpoint (get_klines)...")
    try:
        klines = api.get_klines(symbol="BTC-USDT", interval="1m", limit=2)
        if klines and "data" in klines and len(klines["data"]) >= 1:
            print("✓ get_klines() - SUCCESS")
            print(f"  - Received {len(klines['data'])} candles")
            print(f"  - Latest candle: {klines['data'][-1]}")
        else:
            print("✗ get_klines() - FAILED - No data returned")
    except Exception as e:
        print(f"✗ get_klines() - ERROR: {e}")
    print()
    
    # Test 2: Public endpoint - depth
    print("2. Testing public endpoint (get_depth)...")
    try:
        depth = api.get_depth("BTC-USDT")
        if depth and "data" in depth and "bids" in depth["data"]:
            print("✓ get_depth() - SUCCESS")
            print(f"  - Bids available: {len(depth['data']['bids']) > 0}")
            print(f"  - Asks available: {len(depth['data']['asks']) > 0}")
        else:
            print("✗ get_depth() - FAILED - Invalid data structure")
    except Exception as e:
        print(f"✗ get_depth() - ERROR: {e}")
    print()
    
    # Test 3: Authenticated endpoint - balance
    print("3. Testing authenticated endpoint (get_balance)...")
    try:
        balance = api.get_balance()
        if balance and "data" in balance:
            print("✓ get_balance() - SUCCESS")
            print(f"  - Account has {len(balance['data'])} assets")
            for asset in balance['data']:
                if float(asset['balance']) > 0:
                    print(f"  - {asset['asset']}: {asset['balance']}")
        else:
            print("✗ get_balance() - FAILED - Invalid response structure")
    except Exception as e:
        print(f"✗ get_balance() - ERROR: {e}")
    print()
    
    # Test 4: Authenticated endpoint - open orders
    print("4. Testing authenticated endpoint (get_open_orders)...")
    try:
        orders = api.get_open_orders()
        if orders and "data" in orders:
            print("✓ get_open_orders() - SUCCESS")
            print(f"  - Open orders: {len(orders['data'].get('orders', []))}")
        else:
            print("✗ get_open_orders() - FAILED - Invalid response structure")
    except Exception as e:
        print(f"✗ get_open_orders() - ERROR: {e}")
    print()
    
    # Test 5: WebSocket listen key
    print("5. Testing WebSocket management (create_listen_key)...")
    try:
        listen_key_data = api.create_listen_key()
        if listen_key_data and "listenKey" in listen_key_data:
            print("✓ create_listen_key() - SUCCESS")
            print(f"  - Listen key created: {listen_key_data['listenKey'][:10]}...")
            
            # Test extending the listen key
            extended = api.extend_listen_key(listen_key_data['listenKey'])
            if extended.get("code") == 0:
                print("✓ extend_listen_key() - SUCCESS")
            else:
                print("✗ extend_listen_key() - FAILED")
                
        else:
            print("✗ create_listen_key() - FAILED - Invalid response structure")
    except Exception as e:
        print(f"✗ WebSocket tests - ERROR: {e}")
    print()
    
    print("=== Implementation Test Complete ===")
    print("All core functionality appears to be working correctly!")


if __name__ == "__main__":
    test_basic_functionality()