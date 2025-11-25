# Building BingX AI Terminal Executable

## Prerequisites
- Python 3.8 or higher
- All dependencies from requirements.txt installed

## Build Process

### Method 1: Using build script
```bash
python build_exe.py
```

### Method 2: Direct PyInstaller command
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "assets;assets" --add-data "models;models" --collect-all sklearn --collect-all pandas --collect-all numpy --collect-all plotly --collect-all cryptography --collect-all webview --hidden-import sklearn.utils._cython_blas --hidden-import sklearn.neighbors.typedefs --hidden-import sklearn.tree._utils src/main.py -n BingX_AI_Terminal
```

## Output
- Executable: `dist/BingX_AI_Terminal.exe`
- Size: ~40MB
- Requirements: Windows 10/11 (no additional dependencies needed)

## Notes
- The executable will contain all necessary dependencies
- Assets (HTML, CSS, JS) are bundled inside the executable
- The application will run without requiring Python installation
- API keys are encrypted and stored locally on user's machine
