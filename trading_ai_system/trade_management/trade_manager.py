"""
Trading Management Module for AI Trading System
Handles different trading modes, risk management, and position sizing
"""
import pandas as pd
from typing import Dict, List, Optional
import logging
import math

from ..config import (
    TRADING_MODES, 
    AVAILABLE_CAPITAL_PERCENT, 
    TOTAL_BALANCE, 
    MAX_LEVERAGE, 
    STOP_LOSS_PERCENT, 
    TAKE_PROFIT_RATIO,
    MAX_POSITION_SIZE_PERCENT
)
from ..analysis.technical_analysis import TechnicalAnalyzer
from ..api.binance_api import BinanceAPI


class TradeManager:
    def __init__(self, api: BinanceAPI):
        self.api = api
        self.analyzer = TechnicalAnalyzer()
        self.logger = logging.getLogger(__name__)
        self.current_mode = 'scalping'  # Default mode
        self.available_capital = TOTAL_BALANCE * (AVAILABLE_CAPITAL_PERCENT / 100)
        
    def set_trading_mode(self, mode: str):
        """Set the current trading mode (scalping, spot, long_term)"""
        if mode in TRADING_MODES:
            self.current_mode = mode
            self.logger.info(f"Trading mode set to: {mode}")
        else:
            self.logger.error(f"Invalid trading mode: {mode}")
    
    def calculate_position_size(self, entry_price: float, stop_loss_price: float, 
                              balance_portion: float = 0.02) -> float:
        """Calculate position size based on risk management rules"""
        # Risk per trade = balance * risk percentage
        risk_amount = self.available_capital * balance_portion
        
        # Calculate risk per unit (difference between entry and stop loss)
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit == 0:
            return 0.0
        
        # Position size = risk amount / risk per unit
        position_size = risk_amount / risk_per_unit
        
        # Apply maximum position size limit
        max_position_size = (self.available_capital * MAX_POSITION_SIZE_PERCENT / 100) / entry_price
        position_size = min(position_size, max_position_size)
        
        return position_size
    
    def calculate_stop_loss(self, entry_price: float, direction: str, 
                           multiplier: float = 1.0) -> float:
        """Calculate stop loss price based on entry price and direction"""
        risk_percent = STOP_LOSS_PERCENT * multiplier
        
        if direction.lower() == 'long':
            stop_loss = entry_price * (1 - risk_percent / 100)
        else:  # short
            stop_loss = entry_price * (1 + risk_percent / 100)
        
        return stop_loss
    
    def calculate_take_profit(self, entry_price: float, stop_loss_price: float, 
                            ratio: float = TAKE_PROFIT_RATIO, direction: str = 'long') -> float:
        """Calculate take profit price based on stop loss distance"""
        stop_distance = abs(entry_price - stop_loss_price)
        take_profit_distance = stop_distance * ratio
        
        if direction.lower() == 'long':
            take_profit = entry_price + take_profit_distance
        else:  # short
            take_profit = entry_price - take_profit_distance
        
        return take_profit
    
    def get_top_assets(self, count: int = 5) -> List[Dict]:
        """Get top assets based on technical analysis scores"""
        symbols = self.api.get_futures_symbols()
        asset_scores = []
        
        for symbol in symbols[:50]:  # Limit to first 50 for performance
            try:
                # Get data based on current trading mode's timeframe
                timeframe = TRADING_MODES[self.current_mode]['timeframe']
                df = self.api.get_kline_data(symbol, timeframe, 100)
                
                if not df.empty:
                    score = self.analyzer.get_asset_score(df, symbol)
                    asset_scores.append(score)
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
        
        # Sort by total score and return top assets
        asset_scores.sort(key=lambda x: x['total_score'], reverse=True)
        return asset_scores[:count]
    
    def generate_trade_signal(self, symbol: str) -> Optional[Dict]:
        """Generate a complete trade signal with entry/exit points"""
        timeframe = TRADING_MODES[self.current_mode]['timeframe']
        df = self.api.get_kline_data(symbol, timeframe, 100)
        
        if df.empty:
            return None
        
        # Get technical signals
        signals = self.analyzer.generate_signals(df, symbol)
        
        if signals['recommendation'] in ['BUY', 'SELL']:
            current_price = signals['price']
            direction = 'long' if signals['recommendation'] == 'BUY' else 'short'
            
            # Calculate stop loss
            risk_multiplier = TRADING_MODES[self.current_mode]['risk_multiplier']
            stop_loss = self.calculate_stop_loss(current_price, direction, risk_multiplier)
            
            # Calculate take profit
            take_profit = self.calculate_take_profit(current_price, stop_loss, TAKE_PROFIT_RATIO, direction)
            
            # Calculate position size
            position_size = self.calculate_position_size(
                current_price, 
                stop_loss, 
                0.02 * risk_multiplier  # Adjust risk based on trading mode
            )
            
            trade_signal = {
                'symbol': symbol,
                'direction': direction,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size,
                'leverage': MAX_LEVERAGE,
                'confidence': signals['confidence'],
                'signals': signals['signals']
            }
            
            return trade_signal
        
        return None
    
    def execute_trade(self, trade_signal: Dict) -> Dict:
        """Execute a trade based on the trade signal"""
        try:
            symbol = trade_signal['symbol']
            side = 'buy' if trade_signal['direction'] == 'long' else 'sell'
            amount = trade_signal['position_size']
            leverage = trade_signal['leverage']
            
            # Place the order
            order = self.api.place_order(
                symbol=symbol,
                side=side,
                amount=amount,
                order_type='market',
                leverage=leverage
            )
            
            if order:
                self.logger.info(f"Trade executed: {side.upper()} {amount} {symbol} at market price")
                return order
            else:
                self.logger.error("Failed to execute trade")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return {}
    
    def monitor_positions(self) -> List[Dict]:
        """Monitor all open positions and check for exit conditions"""
        # This would typically run in a separate thread or scheduled job
        # For now, we'll just return the positions
        # In a real implementation, this would check if stop loss or take profit levels are hit
        pass
    
    def get_available_capital(self) -> float:
        """Return the available capital for trading"""
        return self.available_capital
    
    def get_trading_mode_info(self) -> Dict:
        """Get information about the current trading mode"""
        return TRADING_MODES[self.current_mode]
    
    def scan_markets(self) -> List[Dict]:
        """Scan markets for potential trading opportunities"""
        top_assets = self.get_top_assets(10)  # Get top 10 assets
        trade_opportunities = []
        
        for asset in top_assets:
            symbol = asset['symbol']
            trade_signal = self.generate_trade_signal(symbol)
            
            if trade_signal and trade_signal['confidence'] > 0.5:  # Only high confidence signals
                trade_opportunities.append(trade_signal)
        
        # Sort by confidence
        trade_opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        return trade_opportunities


# Example usage
if __name__ == "__main__":
    # Note: This would normally be run with valid API keys
    # For demonstration, we'll show how the trade manager works conceptually
    print("Trade Manager module created successfully")
    print(f"Available capital for trading: {TOTAL_BALANCE * (AVAILABLE_CAPITAL_PERCENT / 100)}$")
    print(f"Current trading mode: scalping")
    print("Module ready to manage trades based on technical analysis signals")