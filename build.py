"""
Скрипт для упаковки приложения в .exe с помощью PyInstaller
"""
import os
import subprocess
import sys


def build_application():
    """Упаковка приложения в .exe"""
    print("Начинается упаковка приложения...")
    
    # Проверяем наличие PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller не установлен. Устанавливаем...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Путь к основному файлу приложения
    main_script = "src/main.py"
    
    # Команда для PyInstaller
    build_command = [
        "pyinstaller",
        "--name=FuturesScout",  # Имя приложения
        "--windowed",  # Графическое приложение (без консоли)
        "--onedir",  # Создать один каталог с приложением
        "--add-data=src/ui;ui",  # Добавить папку с UI файлами
        "--add-data=src/models;models",  # Добавить папку с моделями
        "--add-data=src/utils;utils",  # Добавить папку с утилитами
        "--add-data=src/api;api",  # Добавить папку с API
        "--add-data=src/gui;gui",  # Добавить папку с GUI
        "--hidden-import=PyQt6",  # Явно указываем импорты
        "--hidden-import=PyQt6.QtWebEngineWidgets",
        "--hidden-import=PyQt6.QtMultimedia",
        "--hidden-import=sqlalchemy",
        "--hidden-import=xgboost",
        "--hidden-import=cryptography",
        "--hidden-import=numpy",
        "--hidden-import=pandas",
        "--hidden-import=sklearn",
        "--hidden-import=sklearn.tree",
        "--hidden-import=sklearn.linear_model",
        "--hidden-import=sklearn.svm",
        "--collect-all=lightweight_charts",  # Если используется
        "--icon=icon.ico",  # Иконка (если есть)
        main_script
    ]
    
    # Если файла иконки нет, убираем опцию
    if not os.path.exists("icon.ico"):
        build_command.remove("--icon=icon.ico")
    
    print("Выполняется команда:", " ".join(build_command))
    
    try:
        result = subprocess.run(build_command, check=True)
        print("Приложение успешно упаковано!")
        print("Вы можете найти его в папке 'dist/FuturesScout'")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при упаковке: {e}")
        return False
    
    return True


if __name__ == "__main__":
    build_application()