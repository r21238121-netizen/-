#!/usr/bin/env python3
"""
Скрипт для запуска приложения Futures Scout
"""
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main

if __name__ == "__main__":
    main()