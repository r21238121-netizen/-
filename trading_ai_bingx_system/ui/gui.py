import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from models.trading_logic import TradingLogic
from config.config import TOTAL_BALANCE, RISK_CAPITAL_PERCENT, RISK_CAPITAL
import threading
import time

class TradingGUI:
    def __init__(self):
        self.trading_logic = TradingLogic()
        self.root = tk.Tk()
        self.root.title("AI Торговая Система для BingX")
        self.root.geometry("1000x700")
        
        # Переменные для управления
        self.is_running = False
        self.update_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="AI Торговая Система для BingX", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Выбор режима торговли
        ttk.Label(control_frame, text="Режим торговли:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.mode_var = tk.StringVar(value="scalping")
        mode_combo = ttk.Combobox(control_frame, textvariable=self.mode_var, 
                                 values=["scalping", "spot", "long_term"], state="readonly")
        mode_combo.grid(row=0, column=1, padx=(0, 10))
        mode_combo.bind("<<ComboboxSelected>>", self.change_mode)
        
        # Кнопки управления
        self.start_button = ttk.Button(control_frame, text="Запустить", command=self.start_trading)
        self.start_button.grid(row=0, column=2, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="Остановить", command=self.stop_trading)
        self.stop_button.grid(row=0, column=3, padx=(0, 5))
        self.stop_button.config(state="disabled")
        
        self.refresh_button = ttk.Button(control_frame, text="Обновить", command=self.refresh_data)
        self.refresh_button.grid(row=0, column=4)
        
        # Информация о балансе
        balance_frame = ttk.LabelFrame(main_frame, text="Информация о балансе", padding="10")
        balance_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(balance_frame, text=f"Общий баланс: ${TOTAL_BALANCE}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(balance_frame, text=f"Процент риска: {RISK_CAPITAL_PERCENT}%").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(balance_frame, text=f"Капитал для риска: ${RISK_CAPITAL}").grid(row=2, column=0, sticky=tk.W)
        
        # Статус торговли
        status_frame = ttk.LabelFrame(main_frame, text="Статус", padding="10")
        status_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Остановлено")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="red")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Рекомендации
        rec_frame = ttk.LabelFrame(main_frame, text="Торговые рекомендации", padding="10")
        rec_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.recommendations_text = scrolledtext.ScrolledText(rec_frame, height=8)
        self.recommendations_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Рейтинг пар
        rank_frame = ttk.LabelFrame(main_frame, text="Рейтинг торговых пар", padding="10")
        rank_frame.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.rankings_text = scrolledtext.ScrolledText(rank_frame, height=8)
        self.rankings_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Лог событий
        log_frame = ttk.LabelFrame(main_frame, text="Лог событий", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка пропорций
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        rec_frame.columnconfigure(0, weight=1)
        rec_frame.rowconfigure(0, weight=1)
        rank_frame.columnconfigure(0, weight=1)
        rank_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Инициализация данных
        self.refresh_data()
        
    def change_mode(self, event=None):
        """Изменение режима торговли"""
        new_mode = self.mode_var.get()
        try:
            self.trading_logic.set_trade_mode(new_mode)
            self.log_event(f"Режим изменен на: {new_mode}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка изменения режима: {e}")
    
    def start_trading(self):
        """Запуск автоматической торговли"""
        if not self.is_running:
            try:
                self.trading_logic.set_trade_mode(self.mode_var.get())
                self.trading_logic.start_trading()
                self.is_running = True
                self.start_button.config(state="disabled")
                self.stop_button.config(state="enabled")
                self.status_var.set("Запущено")
                self.status_label.config(foreground="green")
                self.log_event("Торговая система запущена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка запуска торговли: {e}")
    
    def stop_trading(self):
        """Остановка автоматической торговли"""
        if self.is_running:
            self.trading_logic.stop_trading()
            self.is_running = False
            self.start_button.config(state="enabled")
            self.stop_button.config(state="disabled")
            self.status_var.set("Остановлено")
            self.status_label.config(foreground="red")
            self.log_event("Торговая система остановлена")
    
    def refresh_data(self):
        """Обновление данных"""
        # Обновляем рекомендации
        try:
            recommendations = self.trading_logic.get_current_recommendations()
            self.recommendations_text.delete(1.0, tk.END)
            
            if recommendations:
                for rec in recommendations[:10]:  # Показываем только первые 10
                    self.recommendations_text.insert(tk.END, 
                        f"{rec['action']} {rec['pair']} по {rec['entry_price']:.4f}\n"
                        f"  Стоп-лосс: {rec['stop_loss']:.4f}, Тейк-профит: {rec['take_profit']:.4f}\n"
                        f"  Уверенность: {rec['confidence']:.2f}, Размер: {rec['position_size']}\n\n")
            else:
                self.recommendations_text.insert(tk.END, "Нет активных рекомендаций")
        except Exception as e:
            self.log_event(f"Ошибка получения рекомендаций: {e}")
        
        # Обновляем рейтинг пар
        try:
            rankings = self.trading_logic.rank_trading_pairs()
            self.rankings_text.delete(1.0, tk.END)
            
            if rankings:
                for i, (pair, score) in enumerate(rankings[:10], 1):  # Показываем топ-10
                    self.rankings_text.insert(tk.END, f"{i}. {pair}: {score:.2f}\n")
            else:
                self.rankings_text.insert(tk.END, "Нет данных для рейтинга")
        except Exception as e:
            self.log_event(f"Ошибка получения рейтинга: {e}")
    
    def log_event(self, message):
        """Логирование события"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)  # Прокрутка к последней строке
    
    def update_loop(self):
        """Цикл обновления данных"""
        while self.is_running:
            try:
                self.refresh_data()
                time.sleep(30)  # Обновление каждые 30 секунд
            except Exception as e:
                self.log_event(f"Ошибка в цикле обновления: {e}")
                break
    
    def run(self):
        """Запуск GUI"""
        self.root.mainloop()

# Запуск приложения
if __name__ == "__main__":
    app = TradingGUI()
    app.run()