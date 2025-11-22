"""
Trading Agent Module
Implements the live trading functionality with risk management
"""

import pandas as pd
import numpy as np
import torch
import joblib
import json
import asyncio
import aiohttp
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os
from cryptography.fernet import Fernet
import sqlite3
import warnings
warnings.filterwarnings('ignore')

class RiskManager:
    """Manages trading risks and position sizing"""
    def __init__(self, config: Dict):
        self.config = config
        self.max_drawdown = config.get('max_drawdown', 0.10)
        self.risk_per_trade = config.get('risk_per_trade', 0.02)
        self.max_position_size = config.get('max_position_size', 0.10)  # 10% of capital
        self.min_atr_threshold = config.get('min_atr_threshold', 0.001)
        self.max_trades_per_pair = config.get('max_trades_per_pair', 1)
        
        # Track current positions and PnL
        self.current_positions = {}
        self.total_capital = config.get('initial_capital', 10000)
        self.max_capital = self.total_capital
        
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                               signal: int, atr: float, pair: str) -> float:
        """Calculate position size based on risk management rules"""
        # Check ATR threshold
        if atr < self.min_atr_threshold:
            return 0  # Don't trade if volatility is too low
        
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss)
        if risk_per_unit == 0:
            return 0  # Avoid division by zero
        
        # Calculate position size based on risk per trade
        risk_amount = self.total_capital * self.risk_per_trade
        position_size = risk_amount / risk_per_unit
        
        # Apply maximum position size limit
        max_size = self.total_capital * self.max_position_size / entry_price
        position_size = min(position_size, max_size)
        
        # Don't allow more than one position per pair
        if pair in self.current_positions and self.current_positions[pair] != 0:
            return 0
        
        return position_size
    
    def update_capital(self, pnl: float):
        """Update account capital after a trade"""
        self.total_capital += pnl
        if self.total_capital > self.max_capital:
            self.max_capital = self.total_capital
    
    def check_drawdown(self) -> bool:
        """Check if drawdown exceeds threshold"""
        current_drawdown = (self.max_capital - self.total_capital) / self.max_capital
        return current_drawdown <= self.max_drawdown

class TradingAgent:
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.config = {
            'model_path': './models/pytorch_model.pth',
            'scaler_path': './models/scaler.pkl',
            'model_config_path': './models/config.json',
            'api_key': '',
            'secret_key': '',
            'base_url': 'https://open-api.bingx.com',
            'pairs': ['BTC-USDT'],
            'timeframe': '1m',
            'initial_capital': 10000,
            'commission_rate': 0.0005,
            'leverage': 1,
            'risk_per_trade': 0.02,
            'max_drawdown': 0.10,
            'min_atr_threshold': 0.001,
            'stop_loss_atr_multiple': 2,
            'take_profit_atr_multiple': 3,
            'trading_log_path': './logs/trading_log.db',
            'max_trades_per_pair': 1
        }
        
        # Load config if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config.update(json.load(f))
        
        # Initialize components
        self.risk_manager = RiskManager(self.config)
        self.model = None
        self.scaler = None
        self.model_config = None
        self.session = None
        self.encrypted_keys = None
        
        # Initialize trading log database
        self.init_trading_log()
        
        # Load model and scaler
        self.load_model()
    
    def init_trading_log(self):
        """Initialize SQLite database for trading logs"""
        conn = sqlite3.connect(self.config['trading_log_path'])
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair TEXT NOT NULL,
                entry_time TIMESTAMP,
                exit_time TIMESTAMP,
                entry_price REAL,
                exit_price REAL,
                position_size REAL,
                side TEXT,
                pnl REAL,
                commission REAL,
                stop_loss REAL,
                take_profit REAL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair TEXT NOT NULL UNIQUE,
                entry_time TIMESTAMP,
                entry_price REAL,
                position_size REAL,
                side TEXT,
                stop_loss REAL,
                take_profit REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_model(self):
        """Load trained model and scaler"""
        try:
            # Load model config
            with open(self.config['model_config_path'], 'r') as f:
                self.model_config = json.load(f)
            
            # Load scaler
            self.scaler = joblib.load(self.config['scaler_path'])
            
            # Load model based on type
            if self.model_config['model_type'] in ['cnn_lstm', 'transformer']:
                checkpoint = torch.load(self.config['model_path'], map_location=torch.device('cpu'))
                
                if self.model_config['model_type'] == 'cnn_lstm':
                    from models.trainer import CNNLSTMModel
                    self.model = CNNLSTMModel(
                        input_size=len(self.model_config['feature_columns']),
                        num_classes=3,
                        sequence_length=self.model_config['sequence_length']
                    )
                else:  # transformer
                    from models.trainer import TransformerModel
                    self.model = TransformerModel(
                        input_size=len(self.model_config['feature_columns']),
                        num_classes=3,
                        sequence_length=self.model_config['sequence_length']
                    )
                
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.model.eval()
                
            else:  # lightgbm
                import lightgbm as lgb
                self.model = lgb.Booster(model_file=self.config['model_path'])
            
            self.logger.info(f"Model loaded successfully from {self.config['model_path']}")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise
    
    def encrypt_keys(self, api_key: str, secret_key: str) -> Tuple[bytes, bytes]:
        """Encrypt API keys using Fernet"""
        key = Fernet.generate_key()
        fernet = Fernet(key)
        
        encrypted_api_key = fernet.encrypt(api_key.encode())
        encrypted_secret_key = fernet.encrypt(secret_key.encode())
        
        return key, encrypted_api_key, encrypted_secret_key
    
    def decrypt_keys(self, key: bytes, encrypted_api_key: bytes, encrypted_secret_key: bytes) -> Tuple[str, str]:
        """Decrypt API keys"""
        fernet = Fernet(key)
        
        api_key = fernet.decrypt(encrypted_api_key).decode()
        secret_key = fernet.decrypt(encrypted_secret_key).decode()
        
        return api_key, secret_key
    
    def create_session(self):
        """Create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def preprocess_features(self, df: pd.DataFrame) -> np.ndarray:
        """Preprocess features for model prediction"""
        from data.preprocessor import DataPreprocessor
        
        preprocessor = DataPreprocessor()
        processed_df = preprocessor.calculate_features(df)
        
        # Select feature columns used during training
        feature_cols = self.model_config['feature_columns']
        available_cols = [col for col in feature_cols if col in processed_df.columns]
        
        X = processed_df[available_cols].values
        X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def predict_signal(self, features: np.ndarray) -> int:
        """Generate trading signal from model prediction"""
        if self.model_config['model_type'] in ['cnn_lstm', 'transformer']:
            # For sequence models, we need to create sequences
            seq_len = self.model_config['sequence_length']
            
            if len(features) < seq_len:
                return 0  # Not enough data for prediction
            
            # Take the last sequence
            sequence = features[-seq_len:].reshape(1, seq_len, -1)
            sequence_tensor = torch.FloatTensor(sequence)
            
            with torch.no_grad():
                output = self.model(sequence_tensor)
                prediction = torch.argmax(output, dim=1).item()
            
            # Map prediction to trading signal: 0->HOLD, 1->LONG, 2->SHORT
            signal_map = {0: 0, 1: 1, 2: -1}  # HOLD, LONG, SHORT
            return signal_map[prediction]
        else:
            # For LightGBM model
            pred_proba = self.model.predict(features[-1:].reshape(1, -1))  # Use last row
            prediction = np.argmax(pred_proba[0])
            
            # Map prediction to trading signal: 0->HOLD, 1->LONG, 2->SHORT
            signal_map = {0: 0, 1: 1, 2: -1}  # HOLD, LONG, SHORT
            return signal_map[prediction]
    
    async def get_klines(self, pair: str, interval: str, limit: int = 500) -> pd.DataFrame:
        """Fetch klines data from BingX API"""
        await self.create_session()
        
        url = f"{self.config['base_url']}/openApi/quote/v1/klines"
        params = {
            'symbol': pair.replace('-', ''),
            'interval': interval,
            'limit': limit
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data:
                        klines = []
                        for item in data['data']:
                            kline = {
                                'timestamp': int(item[0]),
                                'open': float(item[1]),
                                'high': float(item[2]),
                                'low': float(item[3]),
                                'close': float(item[4]),
                                'volume': float(item[5]),
                                'close_time': int(item[6]),
                                'quote_asset_volume': float(item[7]),
                                'number_of_trades': int(item[8]),
                                'taker_buy_base_asset_volume': float(item[9]),
                                'taker_buy_quote_asset_volume': float(item[10])
                            }
                            klines.append(kline)
                        
                        df = pd.DataFrame(klines)
                        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
                        df.set_index('datetime', inplace=True)
                        
                        return df
                    else:
                        self.logger.error(f"No data in response: {data}")
                        return pd.DataFrame()
                else:
                    self.logger.error(f"Error fetching klines: {response.status}")
                    error_text = await response.text()
                    self.logger.error(f"Error details: {error_text}")
                    return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Exception in get_klines: {e}")
            return pd.DataFrame()
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = np.max(pd.concat([high_low, high_close, low_close], axis=1), axis=1)
        atr = true_range.rolling(period).mean().iloc[-1]
        return atr if not pd.isna(atr) else 0.001  # Return small value if ATR is NaN
    
    async def place_order(self, pair: str, side: str, quantity: float, price: float = None) -> Dict:
        """Place order on BingX (simulated for now)"""
        # In a real implementation, this would interact with the BingX API
        # For now, we'll simulate the order placement
        
        self.logger.info(f"Simulated order - Pair: {pair}, Side: {side}, Quantity: {quantity}, Price: {price}")
        
        return {
            'success': True,
            'order_id': f"SIM_{int(time.time())}",
            'pair': pair,
            'side': side,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now()
        }
    
    def log_trade(self, pair: str, entry_time: datetime, exit_time: datetime, 
                  entry_price: float, exit_price: float, position_size: float, 
                  side: str, pnl: float, commission: float, stop_loss: float, 
                  take_profit: float, reason: str):
        """Log trade to database"""
        conn = sqlite3.connect(self.config['trading_log_path'])
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades 
            (pair, entry_time, exit_time, entry_price, exit_price, position_size, side, pnl, commission, stop_loss, take_profit, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pair, entry_time, exit_time, entry_price, exit_price, position_size, side, pnl, commission, stop_loss, take_profit, reason))
        
        conn.commit()
        conn.close()
    
    def update_position(self, pair: str, entry_time: datetime = None, entry_price: float = None, 
                       position_size: float = None, side: str = None, 
                       stop_loss: float = None, take_profit: float = None):
        """Update position in database"""
        conn = sqlite3.connect(self.config['trading_log_path'])
        cursor = conn.cursor()
        
        if entry_time is None:  # Remove position
            cursor.execute('DELETE FROM positions WHERE pair = ?', (pair,))
        else:  # Update or insert position
            cursor.execute('''
                INSERT OR REPLACE INTO positions 
                (pair, entry_time, entry_price, position_size, side, stop_loss, take_profit)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (pair, entry_time, entry_price, position_size, side, stop_loss, take_profit))
        
        conn.commit()
        conn.close()
    
    async def run_strategy(self, pair: str):
        """Run trading strategy for a single pair"""
        self.logger.info(f"Starting trading strategy for {pair}")
        
        while True:
            try:
                # Fetch latest market data
                df = await self.get_klines(pair, self.config['timeframe'], limit=500)
                
                if df.empty or len(df) < 50:  # Need sufficient data
                    self.logger.warning(f"Not enough data for {pair}, waiting...")
                    await asyncio.sleep(60)  # Wait 1 minute
                    continue
                
                # Preprocess features
                features = self.preprocess_features(df)
                
                if len(features) == 0:
                    self.logger.warning(f"No features extracted for {pair}, waiting...")
                    await asyncio.sleep(60)
                    continue
                
                # Get trading signal
                signal = self.predict_signal(features)
                
                # Get current price and ATR
                current_price = df['close'].iloc[-1]
                atr = self.calculate_atr(df)
                
                self.logger.info(f"Signal for {pair}: {signal}, Price: {current_price}, ATR: {atr}")
                
                # Check if we should enter a position
                if signal != 0:  # If there's a signal (LONG or SHORT)
                    # Calculate position size using risk management
                    atr_multiple = self.config['stop_loss_atr_multiple']
                    if signal == 1:  # LONG
                        stop_loss = current_price - (atr * atr_multiple)
                        side = 'LONG'
                    else:  # SHORT
                        stop_loss = current_price + (atr * atr_multiple)
                        side = 'SHORT'
                    
                    position_size = self.risk_manager.calculate_position_size(
                        current_price, stop_loss, signal, atr, pair
                    )
                    
                    if position_size > 0 and self.risk_manager.check_drawdown():
                        # Place order
                        order_result = await self.place_order(pair, side, position_size, current_price)
                        
                        if order_result['success']:
                            # Log the trade
                            self.update_position(
                                pair=pair,
                                entry_time=datetime.now(),
                                entry_price=current_price,
                                position_size=position_size,
                                side=side,
                                stop_loss=stop_loss,
                                take_profit=current_price + (signal * atr * self.config['take_profit_atr_multiple'])
                            )
                            
                            self.logger.info(f"Position opened: {side} {position_size} {pair} at {current_price}")
                
                # Check for exit conditions for any existing positions
                # (This would be more complex in a real implementation)
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in strategy for {pair}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def run(self):
        """Main trading loop"""
        self.logger.info("Starting trading agent...")
        
        # Check if we have API keys (for real trading)
        if not self.config.get('api_key') or not self.config.get('secret_key'):
            self.logger.warning("API keys not provided. Running in simulation mode.")
        
        # Run strategy for each pair
        tasks = []
        for pair in self.config['pairs']:
            task = asyncio.create_task(self.run_strategy(pair))
            tasks.append(task)
        
        # Wait for all tasks to complete (they run indefinitely)
        await asyncio.gather(*tasks)
    
    def stop(self):
        """Stop the trading agent"""
        self.logger.info("Stopping trading agent...")
        # In a real implementation, you would cancel all tasks here

# Example usage
if __name__ == "__main__":
    # Example of how to use the trading agent
    # This would typically be called after model training and backtesting
    agent = TradingAgent()
    print("Trading agent initialized. In practice, call agent.run() to start live trading.")