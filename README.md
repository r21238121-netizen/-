# BingX AI Trading Agent

An autonomous AI trading agent for futures trading on BingX with local model training capabilities.

## Project Overview

This project implements a complete AI trading system with the following components:

1. **Data Collection Module** - Fetches historical OHLCV data from BingX API
2. **Data Preprocessing Module** - Generates technical indicators and target variables
3. **Model Training Module** - Trains both traditional ML (LightGBM) and neural networks (CNN-LSTM, Transformer)
4. **Backtesting Module** - Realistic simulation with commission, slippage, and risk management
5. **Trading Agent Module** - Live trading with risk management
6. **GUI Module** - Graphical interface for all operations

## Features

- **Local Processing**: All data processing, model training, and trading decisions happen locally
- **Multiple Model Types**: Support for LightGBM, CNN-LSTM, and Transformer models
- **Risk Management**: Position sizing, stop losses, drawdown limits
- **Technical Indicators**: EMA, RSI, MACD, ATR, Bollinger Bands, and more
- **Backtesting**: Comprehensive backtesting with realistic execution simulation
- **GUI Interface**: Tabbed interface for data, training, backtesting, and live trading

## Architecture

```
src/
├── data/           # Data collection and preprocessing
│   ├── data_collector.py
│   └── preprocessor.py
├── models/         # Model training and prediction
│   └── trainer.py
├── backtest/       # Backtesting engine
│   └── backtester.py
├── agent/          # Live trading agent
│   └── trading_agent.py
├── gui/            # Graphical user interface
│   └── main_window.py
├── utils/          # Utilities and configuration
│   └── config.py
└── main.py         # Main application entry point
```

## Configuration

The system is configured through `config.json` which contains settings for:
- Data collection parameters
- Model training parameters
- Backtesting parameters
- Trading parameters
- GUI settings

## Security

- API keys are encrypted using Fernet (AES 256)
- No external cloud services used
- All data remains on the local machine
- Secure storage of trading logs

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py --mode gui  # For GUI
python src/main.py --mode data  # For data collection only
python src/main.py --mode train  # For training only
python src/main.py --mode backtest  # For backtesting only
python src/main.py --mode trade  # For live trading only
```

## Technical Implementation Details

### Data Collection
- Fetches OHLCV data from BingX REST API
- Supports multiple timeframes (1m, 5m, 15m, 1h, 4h, 1d)
- Stores data in Parquet format for efficient access
- Maintains data logs in SQLite database

### Feature Engineering
- Technical indicators: EMA, RSI, MACD, ATR, Bollinger Bands
- Lag features and rolling statistics
- Normalized price movements
- Volatility measures
- Trend indicators

### Target Generation
- Classification targets (LONG, SHORT, HOLD) based on future price movements
- Regression targets for price change prediction
- Commission-adjusted targets to account for trading costs

### Model Architecture
- **LightGBM**: Fast, interpretable gradient boosting for baseline
- **CNN-LSTM**: 1D CNN for feature extraction followed by LSTM for sequence modeling
- **Transformer**: Self-attention mechanism for capturing long-term dependencies

### Risk Management
- Position sizing based on ATR and risk percentage
- Stop loss and take profit levels
- Maximum drawdown limits
- Volatility filters
- One position per pair limit

### Backtesting
- Realistic execution simulation
- Commission and slippage modeling
- Drawdown tracking
- Performance metrics calculation (Sharpe ratio, profit factor, win rate)
- Equity curve visualization

## Performance Considerations

- Model training optimized for 1 year of 1m data in under 1 hour
- Real-time inference under 200ms
- Efficient data processing with pandas and numpy
- Memory-efficient data storage with Parquet

## Safety Features

- Maximum drawdown stop-out
- Risk-per-trade limits
- Volatility-based entry filters
- Position size limits
- Comprehensive logging and monitoring

## Future Enhancements

- WebSocket integration for real-time data
- Reinforcement learning model
- Ensemble methods combining multiple models
- Advanced risk management features
- Performance optimization for GPU inference