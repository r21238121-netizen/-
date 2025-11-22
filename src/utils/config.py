"""
Configuration management for the trading agent
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """Manages configuration for the trading agent"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or './config.json'
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            "data": {
                "pairs": ["BTC-USDT"],
                "timeframes": ["1m", "5m", "15m", "1h"],
                "db_path": "./data/trading_data.db",
                "parquet_path": "./data/parquet/",
                "data_limit": 1000
            },
            "model": {
                "model_type": "lightgbm",
                "target_column": "target_classification_5",
                "feature_columns": [],
                "sequence_length": 10,
                "batch_size": 64,
                "epochs": 100,
                "learning_rate": 0.001,
                "early_stopping_rounds": 10,
                "model_save_path": "./models/",
                "scaler_save_path": "./models/scaler.pkl",
                "model_config_path": "./models/config.json"
            },
            "backtest": {
                "initial_capital": 10000,
                "commission_rate": 0.0005,
                "slippage_rate": 0.001,
                "risk_per_trade": 0.02,
                "max_drawdown": 0.10,
                "min_atr_threshold": 0.01,
                "leverage": 1,
                "results_path": "./results/",
                "plots_path": "./results/plots/"
            },
            "trading": {
                "api_key": "",
                "secret_key": "",
                "base_url": "https://open-api.bingx.com",
                "pairs": ["BTC-USDT"],
                "timeframe": "1m",
                "initial_capital": 10000,
                "commission_rate": 0.0005,
                "leverage": 1,
                "risk_per_trade": 0.02,
                "max_drawdown": 0.10,
                "min_atr_threshold": 0.001,
                "stop_loss_atr_multiple": 2,
                "take_profit_atr_multiple": 3,
                "trading_log_path": "./logs/trading_log.db",
                "max_trades_per_pair": 1
            },
            "gui": {
                "window_width": 1200,
                "window_height": 800,
                "theme": "default"
            }
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
                # Merge user config with defaults
                for section in default_config:
                    if section in user_config:
                        default_config[section].update(user_config[section])
        
        # Ensure directories exist
        self._create_directories(default_config)
        
        return default_config
    
    def _create_directories(self, config: Dict[str, Any]):
        """Create directories specified in config if they don't exist"""
        directories = [
            config['data']['parquet_path'],
            config['model']['model_save_path'],
            config['backtest']['results_path'],
            config['backtest']['plots_path'],
            os.path.dirname(config['model']['scaler_save_path']),
            os.path.dirname(config['model']['model_config_path']),
            os.path.dirname(config['trading']['trading_log_path'])
        ]
        
        for directory in directories:
            if directory:  # Check if directory is not empty
                Path(directory).mkdir(parents=True, exist_ok=True)
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        # Create directory if it doesn't exist
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, section: str, key: str = None):
        """Get configuration value"""
        if key is None:
            return self.config.get(section, {})
        return self.config.get(section, {}).get(key)
    
    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

# Global configuration instance
config_manager = ConfigManager()

def get_config(section: str, key: str = None):
    """Get configuration value from global config manager"""
    return config_manager.get(section, key)

def set_config(section: str, key: str, value: Any):
    """Set configuration value in global config manager"""
    config_manager.set(section, key, value)