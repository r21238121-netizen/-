#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для создания исполняемого файла AI-торговой системы для BingX
"""

import os
import sys
from cx_Freeze import setup, Executable

# Опции для cx_Freeze
build_exe_options = {
    "packages": ["tkinter", "requests", "pandas", "numpy", "sklearn", "matplotlib"],
    "excludes": ["tkinter.test", "unittest"],
    "include_files": [],
    "optimize": 2
}

# Определение исполняемого файла
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Использовать это для GUI приложений, чтобы избежать консольного окна

executables = [
    Executable(
        "run_trading_ai.py",
        base=base,
        target_name="BingX_Trading_AI.exe",
        icon=None  # Можно добавить путь к иконке
    )
]

setup(
    name="BingX Trading AI",
    version="1.0",
    description="AI-торговая система для BingX",
    options={"build_exe": build_exe_options},
    executables=executables
)