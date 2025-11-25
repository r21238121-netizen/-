"""
Test script for the updated BingX client
"""
import asyncio
from bingx_client_updated import BingXClient


async def test_client():
    """
    Test the updated BingX client functionality
    """
    print("Testing Updated BingX Client...\n")
    
    # Initialize client
    client = BingXClient(mode="swap")
    
    try:
        # Test 1: Get ticker
        print("1. Testing ticker retrieval...")
        ticker = await client.get_ticker("BTC-USDT")
        print(f"   BTC-USDT ticker: {ticker}")
        print()

        # Test 2: Get balance (will fail with demo keys, but should not crash)
        print("2. Testing balance retrieval (expected to fail with demo keys)...")
        try:
            balance = await client.get_balance()
            print(f"   Balance: {balance}")
        except Exception as e:
            print(f"   Expected error with demo keys: {e}")
        print()

        # Test 3: Get positions (will fail with demo keys, but should not crash)
        print("3. Testing positions retrieval (expected to fail with demo keys)...")
        try:
            positions = await client.get_positions()
            print(f"   Positions: {positions}")
        except Exception as e:
            print(f"   Expected error with demo keys: {e}")
        print()

        # Test 4: Get PnL (will fail with demo keys, but should not crash)
        print("4. Testing PnL retrieval (expected to fail with demo keys)...")
        try:
            pnl = await client.get_pnl("BTC-USDT")
            print(f"   PnL: {pnl}")
        except Exception as e:
            print(f"   Expected error with demo keys: {e}")
        print()

        # Test 5: Get klines
        print("5. Testing klines retrieval...")
        klines = await client.get_klines("BTC-USDT", "1m", 5)
        print(f"   Klines: {len(klines.get('data', []))} candles retrieved")
        print()

        # Test 6: Get orderbook
        print("6. Testing orderbook retrieval...")
        orderbook = await client.get_orderbook("BTC-USDT")
        print(f"   Orderbook: {orderbook.get('code', 'No code')} - {orderbook.get('msg', 'No message')}")
        print()

        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the session
        await client.close()


if __name__ == "__main__":
    asyncio.run(test_client())