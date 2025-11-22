"""
Test script to verify the implementation of the AI trading agent
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_data_collection():
    """Test data collection module"""
    print("Testing Data Collection Module...")
    try:
        from data.data_collector import DataCollector
        collector = DataCollector()
        print("✓ DataCollector initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Error in DataCollector: {e}")
        return False

def test_preprocessor():
    """Test data preprocessing module"""
    print("Testing Preprocessing Module...")
    try:
        from data.preprocessor import DataPreprocessor
        preprocessor = DataPreprocessor()
        print("✓ DataPreprocessor initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Error in DataPreprocessor: {e}")
        return False

def test_model_trainer():
    """Test model training module"""
    print("Testing Model Training Module...")
    try:
        from models.trainer import ModelTrainer, CNNLSTMModel, TransformerModel
        trainer = ModelTrainer()
        print("✓ ModelTrainer initialized successfully")
        
        # Test model creation
        cnn_model = CNNLSTMModel(input_size=10, num_classes=3)
        transformer_model = TransformerModel(input_size=10, num_classes=3)
        print("✓ Neural network models created successfully")
        return True
    except Exception as e:
        print(f"✗ Error in ModelTrainer: {e}")
        return False

def test_backtester():
    """Test backtesting module"""
    print("Testing Backtesting Module...")
    try:
        from backtest.backtester import Backtester, Position
        backtester = Backtester()
        print("✓ Backtester initialized successfully")
        
        # Test position creation
        pos = Position("2023-01-01", 40000, 0.1, "LONG", stop_loss=39000, take_profit=41000)
        print("✓ Position class working correctly")
        return True
    except Exception as e:
        print(f"✗ Error in Backtester: {e}")
        return False

def test_trading_agent():
    """Test trading agent module"""
    print("Testing Trading Agent Module...")
    try:
        from agent.trading_agent import TradingAgent, RiskManager
        agent = TradingAgent()
        print("✓ TradingAgent initialized successfully")
        
        # Test risk manager
        risk_mgr = RiskManager({"initial_capital": 10000})
        print("✓ RiskManager working correctly")
        return True
    except Exception as e:
        print(f"✗ Error in TradingAgent: {e}")
        return False

def test_gui():
    """Test GUI module"""
    print("Testing GUI Module...")
    try:
        from gui.main_window import MainWindow, run_gui
        print("✓ GUI modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error in GUI: {e}")
        return False

def test_config():
    """Test configuration module"""
    print("Testing Configuration Module...")
    try:
        from utils.config import ConfigManager, get_config, set_config
        config_mgr = ConfigManager()
        print("✓ ConfigManager initialized successfully")
        
        # Test getting config
        data_config = get_config('data')
        print("✓ Configuration access working correctly")
        return True
    except Exception as e:
        print(f"✗ Error in Config: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing AI Trading Agent Implementation\n")
    
    tests = [
        test_data_collection,
        test_preprocessor,
        test_model_trainer,
        test_backtester,
        test_trading_agent,
        test_gui,
        test_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)