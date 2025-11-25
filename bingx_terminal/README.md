# BingX Local AI Trading Terminal

A sophisticated, locally-run trading terminal for BingX futures with integrated AI analysis capabilities. This application provides a complete trading interface with AI-powered signals, all running on your local machine without cloud dependencies.

## Features

- **Local Execution**: Runs entirely on your machine with no cloud dependencies
- **AI-Powered Signals**: Machine learning model for BUY/SELL/HOLD recommendations
- **Real-time Data**: Live market data, order book, and trading functionality
- **Demo Mode**: Practice trading with virtual funds
- **Secure**: AES-256 encryption for API keys stored locally
- **Modular Interface**: Draggable panels for customizable workspace
- **Multi-Asset Support**: Trade BTC, ETH, SOL, BNB, XRP and more futures pairs

## Technical Architecture

- **Backend**: Python with requests, pandas, scikit-learn
- **Frontend**: HTML/CSS/JavaScript with Plotly for charts
- **AI Model**: Random Forest classifier with technical indicators
- **UI Framework**: PyWebView for desktop application
- **Security**: Fernet encryption for API credentials

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bingx-terminal
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Train the AI model:
```bash
python src/train_model.py
```

4. Run the application:
```bash
python src/main.py
```

## Configuration

1. Obtain API credentials from BingX
2. Launch the application
3. Click "Connect" and enter your API key and secret
4. Choose between live or demo mode
5. Start trading with AI assistance

## AI Model Details

The AI model uses several technical indicators to predict market movements:

- **RSI (Relative Strength Index)**
- **MACD (Moving Average Convergence Divergence)**
- **Bollinger Bands**
- **Moving Averages**
- **Volume Indicators**
- **Price Action Features**

The model is trained on historical kline data and continuously improves with new market data.

## Security

- API keys are encrypted using Fernet (AES 128) before storage
- Keys are stored only locally on your machine
- No external services receive your credentials
- All data processing happens locally

## Building Executable

To create a standalone executable for distribution:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "assets;assets" src/main.py -n BingX_AI_Terminal
```

## API Endpoints Used

The application connects to BingX using the following endpoints:

### Account & Balance
- `/openApi/swap/v3/user/balance`
- `/openApi/swap/v2/user/positions`
- `/openApi/swap/v2/user/income`

### Trading
- `/openApi/swap/v2/trade/order`
- `/openApi/swap/v2/trade/order` (cancel)
- `/openApi/swap/v1/trade/closePosition`

### Market Data
- `/openApi/swap/v2/quote/klines`
- `/openApi/swap/v2/quote/depth`
- `/openApi/swap/v2/quote/ticker`

## Disclaimer

This software is for educational and personal use only. Trading futures involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Use at your own risk.

## License

This project is licensed under the MIT License - see the LICENSE file for details.