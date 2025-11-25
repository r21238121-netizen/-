#!/usr/bin/env python
import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    """Build the BingX AI Terminal executable"""
    print("Building BingX Local AI Trading Terminal executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Define the build command
    build_command = [
        "pyinstaller",
        "--onefile",           # Create a single executable file
        "--windowed",          # Don't open console window (for GUI app)
        "--name", "BingX_AI_Terminal",  # Name of the executable
        "--add-data", "assets;assets",  # Include assets folder
        "--add-data", "models;models",  # Include models folder (if any pre-trained models)
        "--collect-all", "sklearn",    # Include all sklearn components
        "--collect-all", "pandas",     # Include all pandas components
        "--collect-all", "numpy",      # Include all numpy components
        "--collect-all", "plotly",     # Include all plotly components
        "--collect-all", "cryptography", # Include cryptography components
        "--collect-all", "webview",    # Include webview components
        "--hidden-import", "sklearn.utils._cython_blas",
        "--hidden-import", "sklearn.neighbors.typedefs",
        "--hidden-import", "sklearn.tree._utils",
        "src/main.py"
    ]
    
    print("Running build command:")
    print(" ".join(build_command))
    
    # Execute the build command
    result = subprocess.run(build_command)
    
    if result.returncode == 0:
        print("\nBuild completed successfully!")
        print("Executable created in 'dist' folder")
        print("Size should be approximately 40MB as specified")
    else:
        print("\nBuild failed!")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()
