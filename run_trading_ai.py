#!/usr/bin/env python3
"""
Entry point script for the AI Trading System
"""
import sys
import os

# Add the trading_ai_system directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'trading_ai_system'))

from trading_ai_system.gui.main_window import run_gui

if __name__ == "__main__":
    print("Starting AI Trading System...")
    print("Please make sure you have installed the required packages:")
    print("pip install -r trading_ai_system/requirements.txt")
    print("\nNote: You will need to set your Binance API keys in the config before trading.")
    print("\nLoading GUI...")
    
    run_gui()