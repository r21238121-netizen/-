# Конфигурационный файл для AI-торговой системы BingX

# BingX API настройки
BINGX_API_KEY = ""  # Замените на ваш API-ключ
BINGX_SECRET_KEY = ""  # Замените на ваш секретный ключ
BINGX_BASE_URL = "https://open-api.bingx.com"

# Настройки торговли
TRADE_MODES = {
    "scalping": {
        "timeframe": "1m",
        "interval_seconds": 30,
        "risk_multiplier": 0.01,  # 1% риска на сделку
        "leverage": 10
    },
    "spot": {
        "timeframe": "15m", 
        "interval_seconds": 300,
        "risk_multiplier": 0.02,  # 2% риска на сделку
        "leverage": 5
    },
    "long_term": {
        "timeframe": "1h",
        "interval_seconds": 1800,
        "risk_multiplier": 0.03,  # 3% риска на сделку
        "leverage": 3
    }
}

# Управление капиталом
TOTAL_BALANCE = 100  # Общий баланс
RISK_CAPITAL_PERCENT = 29  # Процент капитала для торговли (29% от 100$ = 29$)
RISK_CAPITAL = TOTAL_BALANCE * (RISK_CAPITAL_PERCENT / 100)

# Параметры ИИ
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_STD = 2

# Настройки индикаторов
INDICATOR_SETTINGS = {
    "rsi_period": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bb_period": 20,
    "bb_std": 2,
    "stoch_k": 14,
    "stoch_d": 3,
    "ema_short": 9,
    "ema_long": 21
}

# Настройки риска
MAX_POSITION_SIZE_PERCENT = 10  # Максимум 10% капитала на одну позицию
STOP_LOSS_PERCENT = 2  # Стоп-лосс 2%
TAKE_PROFIT_PERCENT = 4  # Тейк-профит 4%
MAX_DRAWDOWN_PERCENT = 10  # Максимальная просадка 10%

# Список торгуемых пар
TRADING_PAIRS = [
    "BTC-USDT", 
    "ETH-USDT", 
    "BNB-USDT", 
    "XRP-USDT", 
    "ADA-USDT",
    "SOL-USDT",
    "DOT-USDT",
    "LINK-USDT"
]

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FILE = "trading_ai.log"

# Режим работы
AUTO_EXECUTION = False  # True для автоматического исполнения ордеров, False для рекомендаций