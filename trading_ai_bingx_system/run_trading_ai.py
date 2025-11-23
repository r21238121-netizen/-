#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Основной скрипт запуска AI-торговой системы для BingX
"""

import sys
import os
import argparse
from ui.gui import TradingGUI
from models.trading_logic import TradingLogic
from config.config import AUTO_EXECUTION

def main():
    parser = argparse.ArgumentParser(description='AI Торговая система для BingX')
    parser.add_argument('--mode', choices=['scalping', 'spot', 'long_term'], 
                       default='scalping', help='Режим торговли')
    parser.add_argument('--auto-exec', action='store_true', 
                       help='Включить автоматическое выполнение ордеров')
    parser.add_argument('--cli', action='store_true', 
                       help='Запуск в CLI-режиме без GUI')
    
    args = parser.parse_args()
    
    if args.auto_exec:
        # Временно включаем автоматическое выполнение
        from config import config
        config.AUTO_EXECUTION = True
    
    if args.cli:
        # CLI режим
        print("Запуск в CLI-режиме...")
        trading_logic = TradingLogic()
        trading_logic.set_trade_mode(args.mode)
        
        print(f"Текущий режим: {args.mode}")
        print("Нажмите Ctrl+C для остановки")
        
        try:
            trading_logic.start_trading()
            while True:
                pass  # Основной цикл будет в trading_logic
        except KeyboardInterrupt:
            print("\nОстановка торговой системы...")
            trading_logic.stop_trading()
    else:
        # GUI режим
        print("Запуск GUI...")
        app = TradingGUI()
        app.trading_logic.set_trade_mode(args.mode)
        app.run()

if __name__ == "__main__":
    main()