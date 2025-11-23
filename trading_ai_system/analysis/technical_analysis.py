"""
Technical Analysis Module for AI Trading System
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

from ..config import TECHNICAL_INDICATORS

class TechnicalAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_ma(self, data: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    def calculate_ema(self, data: pd.Series, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period).mean()
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        ma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        return upper_band, ma, lower_band
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                            k_period: int = 14, d_period: int = 3, smooth: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_value = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        k_smooth = k_value.rolling(window=smooth).mean()
        d_value = k_smooth.rolling(window=d_period).mean()
        
        return k_smooth, d_value
    
    def detect_support_resistance(self, data: pd.Series, window: int = 10) -> Tuple[List[float], List[float]]:
        """Detect support and resistance levels"""
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(data) - window):
            # Check for local minimum (support)
            if all(data[i] <= data[j] for j in range(i - window, i + window + 1)):
                support_levels.append(data[i])
            
            # Check for local maximum (resistance)
            if all(data[i] >= data[j] for j in range(i - window, i + window + 1)):
                resistance_levels.append(data[i])
        
        return list(set(support_levels)), list(set(resistance_levels))
    
    def analyze_trend(self, data: pd.Series, short_period: int = 10, long_period: int = 20) -> str:
        """Analyze the current trend direction"""
        short_ma = self.calculate_ma(data, short_period)
        long_ma = self.calculate_ma(data, long_period)
        
        if short_ma.iloc[-1] > long_ma.iloc[-1]:
            return "bullish"
        elif short_ma.iloc[-1] < long_ma.iloc[-1]:
            return "bearish"
        else:
            return "sideways"
    
    def calculate_volatility(self, data: pd.Series, period: int = 20) -> pd.Series:
        """Calculate rolling volatility"""
        returns = data.pct_change()
        volatility = returns.rolling(window=period).std() * np.sqrt(252)  # Annualized
        return volatility
    
    def generate_signals(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Generate buy/sell signals based on technical indicators"""
        signals = {
            'symbol': symbol,
            'timestamp': df.index[-1],
            'price': df['close'].iloc[-1],
            'signals': [],
            'confidence': 0.0,
            'recommendation': 'HOLD'
        }
        
        close = df['close']
        high = df['high']
        low = df['low']
        
        # Calculate indicators
        rsi = self.calculate_rsi(close, TECHNICAL_INDICATORS['RSI']['period'])
        macd, macd_signal, macd_hist = self.calculate_macd(close)
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(close)
        stoch_k, stoch_d = self.calculate_stochastic(high, low, close)
        
        # RSI signals
        if rsi.iloc[-1] < TECHNICAL_INDICATORS['RSI']['oversold']:
            signals['signals'].append('RSI_Oversold')
        elif rsi.iloc[-1] > TECHNICAL_INDICATORS['RSI']['overbought']:
            signals['signals'].append('RSI_Overbought')
        
        # MACD signals
        if macd.iloc[-1] > macd_signal.iloc[-1] and macd.iloc[-2] <= macd_signal.iloc[-2]:
            signals['signals'].append('MACD_Bullish_Cross')
        elif macd.iloc[-1] < macd_signal.iloc[-1] and macd.iloc[-2] >= macd_signal.iloc[-2]:
            signals['signals'].append('MACD_Bearish_Cross')
        
        # Bollinger Bands signals
        if close.iloc[-1] < lower_bb.iloc[-1]:
            signals['signals'].append('BB_Undervalued')
        elif close.iloc[-1] > upper_bb.iloc[-1]:
            signals['signals'].append('BB_Overvalued')
        
        # Stochastic signals
        if stoch_k.iloc[-1] < 20 and stoch_k.iloc[-1] > stoch_d.iloc[-1]:
            signals['signals'].append('Stoch_Bullish')
        elif stoch_k.iloc[-1] > 80 and stoch_k.iloc[-1] < stoch_d.iloc[-1]:
            signals['signals'].append('Stoch_Bearish')
        
        # Determine recommendation based on signals
        buy_signals = sum(1 for s in signals['signals'] if any(buy_signal in s for buy_signal in ['RSI_Oversold', 'MACD_Bullish_Cross', 'BB_Undervalued', 'Stoch_Bullish']))
        sell_signals = sum(1 for s in signals['signals'] if any(sell_signal in s for sell_signal in ['RSI_Overbought', 'MACD_Bearish_Cross', 'BB_Overvalued', 'Stoch_Bearish']))
        
        if buy_signals > sell_signals:
            signals['recommendation'] = 'BUY'
            signals['confidence'] = min(1.0, buy_signals / (buy_signals + sell_signals or 1))
        elif sell_signals > buy_signals:
            signals['recommendation'] = 'SELL'
            signals['confidence'] = min(1.0, sell_signals / (buy_signals + sell_signals or 1))
        else:
            signals['confidence'] = 0.0
        
        return signals
    
    def get_asset_score(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Calculate a comprehensive score for an asset based on technical analysis"""
        score = {
            'symbol': symbol,
            'volatility': 0.0,
            'momentum_score': 0.0,
            'trend_strength': 0.0,
            'total_score': 0.0
        }
        
        if df.empty or len(df) < 50:
            return score
        
        close = df['close']
        
        # Calculate volatility
        volatility = self.calculate_volatility(close).iloc[-1]
        score['volatility'] = volatility
        
        # Calculate momentum score (based on RSI)
        rsi = self.calculate_rsi(close)
        current_rsi = rsi.iloc[-1]
        if 30 <= current_rsi <= 70:
            momentum_score = 0.5  # Neutral
        elif current_rsi < 30:
            momentum_score = 1.0  # Oversold (potential buy)
        else:
            momentum_score = 0.0  # Overbought (potential sell)
        score['momentum_score'] = momentum_score
        
        # Calculate trend strength
        short_ma = self.calculate_ma(close, 10)
        long_ma = self.calculate_ma(close, 20)
        if not short_ma.empty and not long_ma.empty:
            if short_ma.iloc[-1] > long_ma.iloc[-1]:
                trend_strength = 1.0  # Bullish
            elif short_ma.iloc[-1] < long_ma.iloc[-1]:
                trend_strength = -1.0  # Bearish
            else:
                trend_strength = 0.0  # Neutral
            score['trend_strength'] = trend_strength
        
        # Calculate total score (weighted combination)
        score['total_score'] = (
            0.3 * score['momentum_score'] + 
            0.4 * abs(score['trend_strength']) + 
            0.3 * min(volatility * 10, 1.0)  # Normalize volatility impact
        )
        
        return score

# Example usage
if __name__ == "__main__":
    analyzer = TechnicalAnalyzer()
    
    # Create sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    sample_data = pd.DataFrame({
        'open': prices + np.random.randn(100) * 0.1,
        'high': prices + abs(np.random.randn(100)) * 0.2,
        'low': prices - abs(np.random.randn(100)) * 0.2,
        'close': prices,
        'volume': np.random.randint(1000, 5000, 100)
    }, index=dates)
    
    # Test technical analysis
    signals = analyzer.generate_signals(sample_data, 'BTCUSDT')
    print(f"Signals for BTCUSDT: {signals}")
    
    asset_score = analyzer.get_asset_score(sample_data, 'BTCUSDT')
    print(f"Asset score for BTCUSDT: {asset_score}")