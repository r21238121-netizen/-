"""
Binance API Integration Module
"""
import ccxt
import pandas as pd
import time
from typing import Dict, List, Optional
import logging

from ..config import BINANCE_API_KEY, BINANCE_API_SECRET

class BinanceAPI:
    def __init__(self):
        """Initialize Binance API connection"""
        self.exchange = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'timeout': 30000,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            }
        })
        self.logger = logging.getLogger(__name__)
        
    def get_futures_symbols(self) -> List[str]:
        """Get all available futures symbols"""
        try:
            markets = self.exchange.load_markets()
            futures_symbols = [symbol for symbol in markets.keys() 
                              if symbol.endswith('USDT') and markets[symbol]['future']]
            return futures_symbols
        except Exception as e:
            self.logger.error(f"Error getting futures symbols: {e}")
            return []
    
    def get_kline_data(self, symbol: str, timeframe: str = '1h', limit: int = 500) -> pd.DataFrame:
        """Get kline/candlestick data for a symbol"""
        try:
            klines = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df.astype(float)
            return df
        except Exception as e:
            self.logger.error(f"Error getting kline data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker data for a symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            self.logger.error(f"Error getting ticker for {symbol}: {e}")
            return {}
    
    def get_account_balance(self) -> Dict:
        """Get account balance information"""
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            self.logger.error(f"Error getting account balance: {e}")
            return {}
    
    def place_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None, 
                   order_type: str = 'market', leverage: int = 1) -> Dict:
        """Place an order on Binance Futures"""
        try:
            # Set leverage
            self.exchange.set_leverage(leverage, symbol)
            
            # Place order
            if order_type.lower() == 'market':
                order = self.exchange.create_order(symbol, 'market', side.lower(), amount)
            else:
                order = self.exchange.create_order(symbol, order_type.lower(), side.lower(), amount, price)
            
            return order
        except Exception as e:
            self.logger.error(f"Error placing order for {symbol}: {e}")
            return {}
    
    def close_position(self, symbol: str) -> Dict:
        """Close position for a symbol"""
        try:
            positions = self.exchange.fetch_positions([symbol])
            for position in positions:
                if position['contracts'] != 0:
                    side = 'sell' if position['side'] == 'long' else 'buy'
                    amount = abs(position['contracts'])
                    order = self.exchange.create_market_sell_order(symbol, amount) if side == 'sell' else self.exchange.create_market_buy_order(symbol, amount)
                    return order
            return {}
        except Exception as e:
            self.logger.error(f"Error closing position for {symbol}: {e}")
            return {}
    
    def get_position(self, symbol: str) -> Dict:
        """Get current position for a symbol"""
        try:
            positions = self.exchange.fetch_positions([symbol])
            for position in positions:
                if position['symbol'] == symbol and position['contracts'] != 0:
                    return position
            return {}
        except Exception as e:
            self.logger.error(f"Error getting position for {symbol}: {e}")
            return {}
    
    def get_funding_rate(self, symbol: str) -> float:
        """Get current funding rate for a symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker.get('info', {}).get('lastFundingRate', 0.0)
        except Exception as e:
            self.logger.error(f"Error getting funding rate for {symbol}: {e}")
            return 0.0

# Example usage
if __name__ == "__main__":
    api = BinanceAPI()
    
    # Test connection
    symbols = api.get_futures_symbols()
    print(f"Available symbols: {len(symbols)}")
    print(f"First 10 symbols: {symbols[:10]}")
    
    # Test getting data for a symbol
    if symbols:
        symbol = symbols[0]
        data = api.get_kline_data(symbol, '1h', 10)
        print(f"Data for {symbol}:")
        print(data)