#!/usr/bin/env python3
"""
Autonomous AI Trading Agent for BingX Futures
Version 2.0 with local model training
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    parser = argparse.ArgumentParser(description='Autonomous AI Trading Agent for BingX Futures')
    parser.add_argument('--mode', choices=['data', 'train', 'backtest', 'trade', 'gui'], 
                       default='gui', help='Operation mode')
    parser.add_argument('--config', type=str, help='Configuration file path')
    
    args = parser.parse_args()
    
    if args.mode == 'data':
        from data.data_collector import DataCollector
        collector = DataCollector()
        collector.run()
    elif args.mode == 'train':
        from models.trainer import ModelTrainer
        trainer = ModelTrainer()
        trainer.train()
    elif args.mode == 'backtest':
        from backtest.backtester import Backtester
        backtester = Backtester()
        backtester.run()
    elif args.mode == 'trade':
        from agent.trading_agent import TradingAgent
        agent = TradingAgent()
        agent.run()
    elif args.mode == 'gui':
        from gui.main_window import run_gui
        run_gui()

if __name__ == "__main__":
    main()