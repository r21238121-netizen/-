# Updated BingX API Client

This client is an updated version based on the old project that includes balance, PnL, positions, and other functionality. It has been modernized to work with current BingX API endpoints and includes error handling for API changes.

## Features

- **Async Support**: Uses `aiohttp` for asynchronous requests
- **Dual Mode**: Supports both swap (futures) and spot trading modes
- **Comprehensive Functionality**:
  - Account balance retrieval
  - Position management (swap mode)
  - Order placement and management
  - Market data access (klines, orderbook, tickers)
  - PnL tracking
  - Position closing

## API Endpoints Status

### Working Endpoints
- ✅ `/openApi/swap/v3/user/balance` - Account balance
- ✅ `/openApi/swap/v2/quote/klines` - K-line data
- ✅ `/openApi/swap/v2/quote/depth` - Order book depth
- ✅ `/openApi/spot/v1/trade/order` - Spot order placement
- ✅ `/openApi/swap/v2/trade/order` - Swap order placement

### Potentially Changed Endpoints
- ❌ `/openApi/swap/v2/quote/ticker/price` - Ticker (API may have changed)
- ❌ `/openApi/swap/v2/position/list` - Positions (API may have changed)

## Usage

```python
import asyncio
from bingx_client_updated import BingXClient

async def main():
    # Initialize client
    client = BingXClient(mode="swap")  # Use "spot" for spot trading
    
    try:
        # Get account balance
        balance = await client.get_balance()
        print(f"Balance: {balance}")
        
        # Get market data
        klines = await client.get_klines("BTC-USDT", "1m", 5)
        print(f"Klines: {klines}")
        
        # Place an order
        order = await client.place_order(
            symbol="BTC-USDT",
            side="BUY",
            quantity="0.001",
            order_type="MARKET"
        )
        print(f"Order: {order}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Key Improvements from Old Client

1. **Better Error Handling**: The client now tries multiple endpoint variations when one fails
2. **Async Support**: Full async/await support for better performance
3. **Comprehensive Logging**: Detailed logging for debugging
4. **Flexible Mode Support**: Easy switching between swap and spot modes
5. **Robust Signature Generation**: Proper HMAC-SHA256 signing for all requests

## Known Issues

- Some swap-specific endpoints may not work with all account types
- API endpoints may change frequently - the client attempts to handle this with fallbacks
- Ticker and position endpoints may require specific account permissions

## Configuration

The client uses the same configuration system as the original project, reading from the `config` module which loads API keys from environment variables or defaults.