# AI Trading System for Futures Contracts

## Overview
This is an AI-powered trading system designed to analyze and trade futures contracts on Binance. The system uses technical analysis indicators to identify trading opportunities and manages risk according to user-defined parameters.

## Features

### Trading Modes
- **Scalping**: High-frequency trading with tight timeframes (1-minute charts)
- **Spot Trading**: Medium-term trading (15-minute charts)
- **Long-term**: Position trading with longer timeframes (1-hour charts)

### Technical Analysis
- Multiple technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Candlestick pattern recognition
- Support and resistance level detection
- Trend analysis

### Risk Management
- Configurable risk percentage (default 29% of $100 balance = $29 available for trading)
- Automatic stop-loss and take-profit calculation
- Position sizing based on risk parameters
- Maximum leverage control

### Asset Selection
- Automatic scanning of all available futures pairs
- Ranking of assets based on trading potential
- Real-time market analysis

## Architecture

### Modules
1. **API Module**: Handles Binance API integration
2. **Analysis Module**: Performs technical analysis
3. **Trade Management**: Handles trading logic and risk management
4. **GUI Module**: User interface for Windows executable

### Configuration
All parameters are defined in `config.py`:
- API keys (to be set by user)
- Trading parameters
- Risk management settings
- Technical indicator settings

## Requirements

### Dependencies
- Python 3.8+
- ccxt
- pandas
- numpy
- scikit-learn
- ta (technical analysis)
- tkinter (for GUI)

### Installation
```bash
pip install -r requirements.txt
```

## Usage

### Running the System
```bash
python -m trading_ai_system.gui.main_window
```

### Building the Executable
```bash
pip install cx_Freeze
python build_exe.py build
```

## Configuration

### API Keys
Before using the system, set your Binance API keys in `config.py`:
```python
BINANCE_API_KEY = "your_api_key_here"
BINANCE_API_SECRET = "your_api_secret_here"
```

### Trading Parameters
- Total Balance: $100 (example)
- Available Capital: 29% of total balance
- Maximum Leverage: Configurable
- Risk per Trade: 2% of available capital

## Important Notes

⚠️ **Risk Warning**: This system is designed for educational purposes. Trading futures involves substantial risk and may not be suitable for all investors. Past performance does not guarantee future results.

⚠️ **API Keys**: Keep your API keys secure and never share them. The system should be used with a separate trading account with funds you can afford to lose.

## Customization

The system is designed to be easily customizable:
- Modify technical indicators in `technical_analysis.py`
- Adjust risk parameters in `config.py`
- Add new trading strategies in `trade_manager.py`
- Customize the GUI in `main_window.py`

## Future Enhancements

Potential improvements include:
- Machine learning model integration
- Backtesting capabilities
- Advanced order types
- Multi-exchange support
- Advanced risk management features