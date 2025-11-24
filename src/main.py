"""
Futures Scout - Локальный ИИ-ассистент для фьючерсной торговли
Основной файл запуска приложения
"""
import sys
import os
import json
import asyncio
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal

from gui.auth_window import AuthWindow
from gui.main_window import MainWindow
from api.bingx_api import BingXAPI
from api.bingx_initializer import initialize_bingx_connection
from models.ai_agent import AIAgent
from utils.config import Config


class FuturesScoutApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.config = Config()
        self.api = None
        self.ai_agent = None
        
    def run(self):
        # Проверяем наличие сохраненных API-ключей
        if self.config.has_saved_credentials():
            # Пробуем подключиться с сохраненными ключами
            api_key, secret_key = self.config.get_saved_credentials()
            self.api = BingXAPI(api_key, secret_key)
            
            if self.api.validate_credentials():
                # Проверяем баланс и другие критерии
                if self.initialize_and_check_criteria():
                    # Успешная инициализация - открываем основное окно
                    self.start_main_window(real_mode=True)
                else:
                    # Не прошли критерии - показываем ошибку и окно аутентификации
                    print("Ошибка: Не выполнены критерии для торговли")
                    self.start_auth_window()
            else:
                # Неверные ключи - показываем окно аутентификации
                print("Ошибка: Неверные API-ключи")
                self.start_auth_window()
        else:
            # Нет сохраненных ключей - запрашиваем ключи у пользователя
            print("Пожалуйста, введите API-ключи для подключения к BingX")
            self.start_auth_window()
    
    def initialize_and_check_criteria(self):
        """
        Инициализация и проверка критериев для торговли
        Возвращает True если все критерии выполнены, иначе False
        """
        try:
            # Используем новый инициализатор для проверки
            result = initialize_bingx_connection(self.api.api_key, self.api.secret_key)
            
            if result['success']:
                print(f"Инициализация успешна. Баланс: {result['balance']} USDT, монет с балансом > 0: {result['total_coins_with_balance']}")
                return True
            else:
                print(f"Ошибка инициализации: {result['error']}")
                return False
            
        except Exception as e:
            print(f"Ошибка при инициализации: {e}")
            return False
    
    def start_auth_window(self):
        """Запуск окна аутентификации"""
        self.auth_window = AuthWindow(self)
        self.auth_window.show()
        
    def start_main_window(self, real_mode=True):
        """Запуск основного окна"""
        # Ensure AI agent is initialized
        if self.ai_agent is None:
            self.ai_agent = AIAgent(self.api, demo_mode=not real_mode)
        self.main_window = MainWindow(self.api, self.ai_agent, real_mode)
        self.main_window.show()
        
    def connect_with_credentials(self, api_key, secret_key):
        """Подключение с новыми учетными данными"""
        self.api = BingXAPI(api_key, secret_key)
        if self.api.validate_credentials():
            # Проверяем критерии с помощью нового инициализатора
            result = initialize_bingx_connection(api_key, secret_key)
            if result['success']:
                # Сохраняем ключи
                self.config.save_credentials(api_key, secret_key)
                # Создаем ИИ-агента
                self.ai_agent = AIAgent(self.api)
                # Открываем основное окно
                self.start_main_window(real_mode=True)
                self.auth_window.close()
                return True
            else:
                print(f"Ошибка: Не выполнены критерии для торговли - {result['error']}")
                return False
        else:
            print("Ошибка: Неверные API-ключи")
            return False
    
    def start_demo_mode(self):
        """Запуск демо-режима"""
        self.api = BingXAPI(demo_mode=True)
        self.ai_agent = AIAgent(self.api, demo_mode=True)
        self.start_main_window(real_mode=False)


def main():
    app = FuturesScoutApp()
    app.run()
    sys.exit(app.app.exec())


if __name__ == "__main__":
    main()