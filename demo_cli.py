#!/usr/bin/env python3
"""
Демонстрация CLI-версии приложения с функциональностью инициализации и проверки баланса
"""
import sys
import os

# Добавляем путь к src в sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.ai_agent import AIAgent
from api.bingx_api import BingXAPI
from utils.config import Config


class FuturesScoutCLI:
    def __init__(self):
        self.config = Config()
        self.api = None
        self.ai_agent = None
        
    def run(self):
        print("Futures Scout - Локальный ИИ-ассистент для фьючерсной торговли")
        print("=" * 60)
        
        # Проверяем наличие сохраненных API-ключей
        if self.config.has_saved_credentials():
            print("Найдены сохраненные API-ключи.")
            api_key, secret_key = self.config.get_saved_credentials()
            self.api = BingXAPI(api_key, secret_key)
            
            if self.api.validate_credentials():
                print("Ключи действительны. Проверяем критерии для торговли...")
                if self.initialize_and_check_criteria():
                    print("✅ Инициализация успешна. Доступ к торговле разрешен.")
                    self.start_main_functionality()
                else:
                    print("❌ Не выполнены критерии для торговли.")
                    self.request_credentials()
            else:
                print("❌ Неверные API-ключи.")
                self.request_credentials()
        else:
            print("API-ключи не найдены.")
            self.request_credentials()
    
    def request_credentials(self):
        """Запрос API-ключей у пользователя"""
        print("\nПожалуйста, введите API-ключи для подключения к BingX")
        api_key = input("Введите API-ключ: ").strip()
        secret_key = input("Введите Secret-ключ: ").strip()
        
        if api_key and secret_key:
            self.api = BingXAPI(api_key, secret_key)
            if self.api.validate_credentials():
                print("✅ Ключи подтверждены. Сохраняем...")
                self.config.save_credentials(api_key, secret_key)
                
                if self.initialize_and_check_criteria():
                    print("✅ Инициализация успешна. Доступ к торговле разрешен.")
                    self.start_main_functionality()
                else:
                    print("❌ Не выполнены критерии для торговли.")
            else:
                print("❌ Неверные API-ключи. Пожалуйста, проверьте введенные данные.")
        else:
            print("❌ Ключи не введены. Работа в демо-режиме.")
            self.api = BingXAPI(demo_mode=True)
            self.ai_agent = AIAgent(self.api, demo_mode=True)
            self.start_demo_functionality()
    
    def initialize_and_check_criteria(self):
        """
        Инициализация и проверка критериев для торговли
        Возвращает True если все критерии выполнены, иначе False
        """
        try:
            print("Проверка баланса...")
            balance_data = self.api.get_balance()
            if 'data' not in balance_data or 'balances' not in balance_data['data']:
                print("❌ Не удалось получить баланс")
                return False
            
            # Проверяем USDT баланс
            usdt_balance = 0
            for balance in balance_data['data']['balances']:
                if balance['asset'] == 'USDT':
                    usdt_balance = float(balance['walletBalance'])
                    break
            
            print(f"Баланс: {usdt_balance} USDT")
            
            if usdt_balance <= 0:
                print("❌ Недостаточно средств")
                return False
            
            # Проверяем другие критерии (например, минимальный баланс для торговли)
            if usdt_balance < 10:  # Минимальный порог для торговли
                print(f"❌ Баланс слишком мал для торговли. Требуется минимум 10 USDT")
                return False
            
            # Проверяем возможность получения цен
            market_data = self.api.get_market_price('BTC-USDT')
            if 'data' not in market_data or len(market_data['data']) == 0:
                print("❌ Не удалось получить рыночные данные")
                return False
            
            # Создаем ИИ-агента
            self.ai_agent = AIAgent(self.api, demo_mode=False)
            
            print(f"✅ Инициализация успешна. Баланс: {usdt_balance} USDT")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при инициализации: {e}")
            return False
    
    def start_main_functionality(self):
        """Основная функциональность приложения"""
        print("\n" + "="*60)
        print("ОСНОВНОЕ МЕНЮ ПРИЛОЖЕНИЯ")
        print("="*60)
        
        while True:
            print("\nВыберите действие:")
            print("1. Анализ рынка")
            print("2. Генерация торгового сигнала")
            print("3. Просмотр статистики ИИ")
            print("4. Проверить баланс")
            print("5. Выход")
            
            choice = input("Ваш выбор (1-5): ").strip()
            
            if choice == '1':
                self.analyze_market()
            elif choice == '2':
                self.generate_signal()
            elif choice == '3':
                self.show_ai_stats()
            elif choice == '4':
                self.check_balance()
            elif choice == '5':
                print("До свидания!")
                break
            else:
                print("Неверный выбор. Пожалуйста, выберите от 1 до 5.")
    
    def start_demo_functionality(self):
        """Функциональность в демо-режиме"""
        print("\n" + "="*60)
        print("ДЕМО-РЕЖИМ ПРИЛОЖЕНИЯ")
        print("="*60)
        
        print("Работа в демо-режиме. Все данные фиктивные.")
        
        while True:
            print("\nВыберите действие:")
            print("1. Анализ рынка (демо)")
            print("2. Генерация торгового сигнала (демо)")
            print("3. Просмотр статистики ИИ")
            print("4. Выход")
            
            choice = input("Ваш выбор (1-4): ").strip()
            
            if choice == '1':
                self.analyze_market()
            elif choice == '2':
                self.generate_signal()
            elif choice == '3':
                self.show_ai_stats()
            elif choice == '4':
                print("До свидания!")
                break
            else:
                print("Неверный выбор. Пожалуйста, выберите от 1 до 4.")
    
    def analyze_market(self):
        """Анализ рынка для выбранной монеты"""
        symbol = input("Введите символ монеты (например, BTC-USDT): ").strip()
        if not symbol:
            symbol = "BTC-USDT"  # Значение по умолчанию
        
        print(f"\nАнализ рынка для {symbol}...")
        analysis = self.ai_agent.analyze_market_situation(symbol)
        print(f"\n{analysis}")
        
        # Озвучивание анализа (возвращаем текст)
        speak_text = self.ai_agent.speak_analysis(symbol)
        print(f"\nТекст для озвучивания:")
        print(speak_text)
    
    def generate_signal(self):
        """Генерация торгового сигнала"""
        symbol = input("Введите символ монеты (например, BTC-USDT): ").strip()
        if not symbol:
            symbol = "BTC-USDT"  # Значение по умолчанию
        
        print(f"\nГенерация сигнала для {symbol}...")
        signal = self.ai_agent.generate_signal(symbol)
        
        if signal:
            print(f"\n✅ Сгенерирован сигнал:")
            print(f"  Монета: {signal['coin']}")
            print(f"  Направление: {signal['side']}")
            print(f"  Вход: {signal['entry_price']}")
            print(f"  Тейк-профит: {signal['tp_price']}")
            print(f"  Стоп-лосс: {signal['sl_price']}")
            print(f"  Уверенность: {signal['confidence']:.2%}")
            print(f"  RR соотношение: {signal['rr_ratio']:.2f}")
        else:
            print("❌ Не удалось сгенерировать сигнал. Недостаточно данных или низкая уверенность.")
    
    def show_ai_stats(self):
        """Показать статистику ИИ-агента"""
        stats = self.ai_agent.get_performance_stats()
        print(f"\n📊 Статистика ИИ-агента:")
        print(f"  Всего сигналов: {stats['total_signals']}")
        print(f"  Успешных: {stats['successful_signals']}")
        print(f"  Процент успеха: {stats['win_rate']:.2%}")
        print(f"  Средняя уверенность (успех): {stats['avg_confidence_success']:.2%}")
        print(f"  Средняя уверенность (провал): {stats['avg_confidence_failure']:.2%}")
    
    def check_balance(self):
        """Проверка баланса"""
        try:
            balance_data = self.api.get_balance()
            if 'data' in balance_data and 'balances' in balance_data['data']:
                print(f"\n💰 Баланс аккаунта:")
                for balance in balance_data['data']['balances']:
                    asset = balance['asset']
                    wallet_balance = balance['walletBalance']
                    unrealized_pnl = balance['unrealizedProfit']
                    print(f"  {asset}: {wallet_balance} (PnL: {unrealized_pnl})")
            else:
                print("❌ Не удалось получить баланс")
        except Exception as e:
            print(f"❌ Ошибка получения баланса: {e}")


def main():
    app = FuturesScoutCLI()
    app.run()


if __name__ == "__main__":
    main()