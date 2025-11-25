# BingX API Professional Client

A production-level implementation of the BingX exchange API with secure authentication, rate limiting, and comprehensive error handling.

## Features

- ✅ **Secure Authentication**: Implements HMAC-SHA256 signature generation for API requests
- ⚡ **Rate Limiting**: Built-in rate limiting to prevent exceeding API limits (default: 5 requests/sec)
- 🔄 **Automatic Retries**: Configurable retry mechanism for failed requests
- 🛡️ **Proper Error Handling**: Comprehensive error handling and logging
- 📊 **Full API Coverage**: Support for all major BingX API endpoints
- 📝 **Well Documented**: Full docstrings and examples

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

The API client can be configured via environment variables or the config file:

### Environment Variables
```bash
export BINGX_API_KEY="your_api_key_here"
export BINGX_SECRET_KEY="your_secret_key_here"
export BINGX_DEMO_MODE="true"  # Set to "true" for demo mode
export RATE_LIMIT_DELAY="0.2"  # Delay between requests in seconds
export LOG_LEVEL="INFO"  # Logging level
```

### Default Configuration
By default, the client uses demo keys provided in the code. For real trading, update the keys in `config.py`.

## Usage

### Basic Usage
```python
from bingx_api import BingXAPI
from config import config

# Get credentials from config
credentials = config.get_api_credentials()
api = BingXAPI(
    api_key=credentials['api_key'],
    secret_key=credentials['secret_key']
)

# Get market data (no authentication required)
klines = api.get_klines(symbol="BTC-USDT", interval="1m", limit=100)
print(klines)

# Get account balance (requires authentication)
balance = api.get_balance()
print(balance)
```

### Available Methods

#### Market Data (Public Endpoints)
- `get_klines(symbol, interval, limit)` - Get candlestick data
- `get_ticker(symbol)` - Get current ticker price
- `get_24hr_ticker(symbol)` - Get 24hr ticker statistics 
- `get_depth(symbol)` - Get order book depth
- `get_trades(symbol, limit)` - Get recent trades

#### Trading (Authenticated Endpoints)
- `get_balance()` - Get account balance
- `place_order(symbol, side, order_type, quantity, position_side)` - Place new order
- `cancel_order(symbol, order_id)` - Cancel order
- `get_open_orders(symbol=None)` - Get open orders
- `get_order_history(symbol, start_time, end_time)` - Get order history

#### WebSocket Management
- `create_listen_key()` - Create listen key for private streams
- `extend_listen_key(listen_key)` - Extend listen key validity
- `close_listen_key(listen_key)` - Close listen key

## Security Notes

⚠️ **Important Security Information:**
- Never commit API keys to version control
- Use environment variables for production deployments
- The default keys in this implementation are for testing only
- Always validate and sanitize input parameters
- Monitor your API usage to avoid exceeding rate limits

## Production Deployment

For production use:
1. Set environment variables with your real API keys
2. Configure appropriate rate limiting based on BingX's requirements
3. Implement proper logging and monitoring
4. Use HTTPS for all connections
5. Regularly rotate your API keys

## Error Handling

The client includes comprehensive error handling:
- Automatic retries for transient failures
- Detailed logging for debugging
- Proper exception propagation
- Rate limit enforcement

## Rate Limits

The client enforces BingX's rate limits:
- Default: Maximum 5 requests per second per IP
- Configurable delay between requests
- Automatic backoff for rate limit errors

## Support

For issues and questions, please check:
- BingX API documentation
- This repository's issue tracker
- Rate limit policies and API terms of service