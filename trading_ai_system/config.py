"""
Configuration file for the AI Trading System
"""

# API Configuration
BINANCE_API_KEY = ""
BINANCE_API_SECRET = ""

# Trading Parameters
TOTAL_BALANCE = 100.0  # Total account balance in USD
AVAILABLE_CAPITAL_PERCENT = 29.0  # Percentage of balance available for trading (e.g., 29%)
MAX_LEVERAGE = 10  # Maximum leverage allowed
RISK_PER_TRADE_PERCENT = 2.0  # Risk per trade as percentage of available capital

# Trading Modes
TRADING_MODES = {
    'scalping': {
        'name': 'Scalping',
        'timeframe': '1m',
        'indicators': ['RSI', 'Stochastic', 'Volume'],
        'frequency': 'high',
        'risk_multiplier': 1.0
    },
    'spot': {
        'name': 'Spot Trading',
        'timeframe': '15m',
        'indicators': ['MA', 'MACD', 'Bollinger Bands'],
        'frequency': 'medium',
        'risk_multiplier': 0.7
    },
    'long_term': {
        'name': 'Long Term',
        'timeframe': '1h',
        'indicators': ['EMA', 'MACD', 'Support/Resistance'],
        'frequency': 'low',
        'risk_multiplier': 0.5
    }
}

# Technical Analysis Parameters
TECHNICAL_INDICATORS = {
    'MA': {'period': 20},
    'EMA': {'period': 20},
    'SMA': {'period': 20},
    'RSI': {'period': 14, 'overbought': 70, 'oversold': 30},
    'MACD': {'fast': 12, 'slow': 26, 'signal': 9},
    'BOLLINGER': {'period': 20, 'std_dev': 2},
    'STOCHASTIC': {'k_period': 14, 'd_period': 3, 'smooth': 3}
}

# Risk Management
STOP_LOSS_PERCENT = 5.0  # Default stop loss percentage
TAKE_PROFIT_RATIO = 2.0  # Take profit will be set at 2x stop loss distance
MAX_POSITION_SIZE_PERCENT = 10.0  # Maximum position size as % of available capital

# System Settings
UPDATE_INTERVAL_SECONDS = 1  # How often to check for new signals
LOG_LEVEL = 'INFO'