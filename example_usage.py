"""
Example usage of the BingX AI Trading Agent
This script demonstrates the main workflows of the system
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def example_data_collection():
    """Example of data collection"""
    print("=== Example: Data Collection ===")
    from data.data_collector import DataCollector
    
    # Initialize collector with custom config
    collector = DataCollector()
    
    # For this example, we'll just show the configuration
    print(f"Data collection configured for pairs: {collector.config['pairs']}")
    print(f"Timeframes: {collector.config['timeframes']}")
    print(f"Data will be saved to: {collector.config['parquet_path']}")
    print()

def example_data_preprocessing():
    """Example of data preprocessing"""
    print("=== Example: Data Preprocessing ===")
    from data.preprocessor import DataPreprocessor
    
    # Create a mock dataset for demonstration
    dates = pd.date_range(start='2023-01-01', end='2023-03-01', freq='1D')
    n = len(dates)
    
    mock_data = pd.DataFrame({
        'timestamp': range(len(dates)),
        'datetime': dates,
        'open': 40000 + np.cumsum(np.random.normal(0, 100, n)),
        'high': 40000 + np.cumsum(np.random.normal(0, 100, n)) + np.random.uniform(50, 200, n),
        'low': 40000 + np.cumsum(np.random.normal(0, 100, n)) - np.random.uniform(50, 200, n),
        'close': 40000 + np.cumsum(np.random.normal(0, 100, n)),
        'volume': np.random.uniform(1000, 10000, n)
    })
    
    # Ensure OHLC consistency
    for i in range(1, n):
        mock_data.loc[i, 'open'] = mock_data.loc[i-1, 'close']
        mock_data.loc[i, 'high'] = max(mock_data.loc[i, 'open'], 
                                      mock_data.loc[i, 'close'] + np.random.uniform(0, 100))
        mock_data.loc[i, 'low'] = min(mock_data.loc[i, 'open'], 
                                     mock_data.loc[i, 'close'] - np.random.uniform(0, 100))
    
    # Initialize preprocessor
    preprocessor = DataPreprocessor()
    
    # Process the data
    processed_data = preprocessor.prepare_dataset(mock_data, prediction_horizon=5)
    
    print(f"Original data shape: {mock_data.shape}")
    print(f"Processed data shape: {processed_data.shape}")
    print(f"Number of features created: {len([col for col in processed_data.columns if col.startswith(('ema_', 'rsi_', 'macd_', 'atr_', 'bb_', 'volatility_', 'returns_', 'volume_', 'norm_', 'high_', 'low_', 'price_position_', 'trend_', 'open_close_', 'high_low_') or '_lag_' in col or '_ratio' in col or '_spread' in col)])}")
    print()

def example_model_training():
    """Example of model training"""
    print("=== Example: Model Training ===")
    from models.trainer import ModelTrainer
    
    # Initialize trainer
    trainer = ModelTrainer()
    
    print(f"Model training configured for: {trainer.config['model_type']}")
    print(f"Target column: {trainer.config['target_column']}")
    print(f"Model will be saved to: {trainer.config['model_save_path']}")
    print("Training parameters:")
    print(f"  - Epochs: {trainer.config['epochs']}")
    print(f"  - Batch size: {trainer.config['batch_size']}")
    print(f"  - Learning rate: {trainer.config['learning_rate']}")
    print()

def example_backtesting():
    """Example of backtesting"""
    print("=== Example: Backtesting ===")
    from backtest.backtester import Backtester
    
    # Initialize backtester
    backtester = Backtester()
    
    print(f"Backtesting configured with:")
    print(f"  - Initial capital: ${backtester.config['initial_capital']:,}")
    print(f"  - Commission rate: {backtester.config['commission_rate']:.3%}")
    print(f"  - Risk per trade: {backtester.config['risk_per_trade']:.1%}")
    print(f"  - Max drawdown limit: {backtester.config['max_drawdown']:.1%}")
    print(f"Results will be saved to: {backtester.config['results_path']}")
    print()

def example_trading_agent():
    """Example of trading agent"""
    print("=== Example: Trading Agent ===")
    from agent.trading_agent import TradingAgent
    
    # Initialize agent
    agent = TradingAgent()
    
    print(f"Trading agent configured for pairs: {agent.config['pairs']}")
    print(f"Timeframe: {agent.config['timeframe']}")
    print(f"Leverage: {agent.config['leverage']}x")
    print(f"Risk per trade: {agent.config['risk_per_trade']:.1%}")
    print(f"Max drawdown limit: {agent.config['max_drawdown']:.1%}")
    print("Trading logs will be saved to:", agent.config['trading_log_path'])
    print()

def example_end_to_end_workflow():
    """Example of end-to-end workflow"""
    print("=== Example: End-to-End Workflow ===")
    print("1. Data Collection -> Preprocessing -> Model Training -> Backtesting -> Live Trading")
    print()
    print("Step 1: Collect market data from BingX API")
    print("  - Fetch OHLCV data for configured pairs and timeframes")
    print("  - Store in Parquet format for efficient access")
    print()
    print("Step 2: Preprocess data and generate features")
    print("  - Calculate technical indicators (EMA, RSI, MACD, ATR, etc.)")
    print("  - Generate target variables for training")
    print("  - Split data temporally to prevent data leakage")
    print()
    print("Step 3: Train machine learning model")
    print("  - Choose between LightGBM, CNN-LSTM, or Transformer")
    print("  - Optimize hyperparameters using Optuna")
    print("  - Validate on out-of-sample data")
    print()
    print("Step 4: Backtest strategy")
    print("  - Simulate trading with realistic execution")
    print("  - Account for commissions, slippage, and risk management")
    print("  - Evaluate performance metrics")
    print()
    print("Step 5: Deploy to live trading")
    print("  - Connect to BingX API with encrypted credentials")
    print("  - Execute trades based on model predictions")
    print("  - Monitor risk and performance in real-time")
    print()

def main():
    """Run all examples"""
    print("BingX AI Trading Agent - Example Usage\n")
    
    example_data_collection()
    example_data_preprocessing()
    example_model_training()
    example_backtesting()
    example_trading_agent()
    example_end_to_end_workflow()
    
    print("For actual usage:")
    print("1. Configure your settings in config.json")
    print("2. Run 'python src/main.py --mode gui' for the graphical interface")
    print("3. Or run individual components with --mode data|train|backtest|trade")
    print()
    print("Security Note: When using live trading, ensure your API keys are properly encrypted")

if __name__ == "__main__":
    main()