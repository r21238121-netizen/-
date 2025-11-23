"""
Build script to create an executable for the AI Trading System
"""
import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_options = {
    'packages': [
        'ccxt', 'pandas', 'numpy', 'sklearn', 'ta', 
        'tkinter', 'tkinter.scrolledtext', 'tkinter.messagebox',
        'logging', 'threading', 'datetime'
    ],
    'excludes': [],
    'include_files': []
}

# Base configuration for GUI application
base = 'Win32GUI' if sys.platform == 'win32' else None

# Executable configuration
executables = [
    Executable(
        'gui/main_window.py',
        base=base,
        target_name='AI_Trading_System.exe',
        icon=None  # Add an icon file path if available
    )
]

setup(
    name='AI Trading System',
    version='1.0',
    description='AI-powered trading system for futures contracts',
    options={'build_exe': build_options},
    executables=executables
)