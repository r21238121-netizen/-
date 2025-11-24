"""
Основное окно приложения
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QComboBox, QCheckBox, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QSoundEffect  # Для звуковых уведомлений
import os
from ui.chart_widget import ChartWidget
from ui.orderbook_widget import OrderBookWidget


class MainWindow(QMainWindow):
    def __init__(self, api, ai_agent, real_mode=True):
        super().__init__()
        self.api = api
        self.ai_agent = ai_agent
        self.real_mode = real_mode
        
        # Текущая выбранная пара
        self.current_symbol = 'BTC-USDT'
        
        # Инициализация звуковых эффектов
        self.init_sound_effects()
        
        # Переменные для отслеживания PnL
        self.current_pnl = 0.0
        self.total_pnl = 0.0
        
        self.init_ui()
        self.setup_timers()
    
    def init_sound_effects(self):
        """Инициализация звуковых эффектов"""
        try:
            # Создаем директорию для звуков если не существует
            sound_dir = os.path.join(os.path.expanduser("~"), ".futures_scout", "sounds")
            os.makedirs(sound_dir, exist_ok=True)
            
            # Создаем простой звуковой файл для уведомлений (в реальном приложении можно использовать реальные звуки)
            # Для демонстрации используем системный звук или просто будем выводить сообщение
            self.trade_sound = QSoundEffect(self)
            # В реальном приложении загрузите реальный звуковой файл
            # self.trade_sound.setSource(QUrl.fromLocalFile("/path/to/trade_sound.wav"))
            # self.trade_sound.setVolume(0.5)
        except:
            # Если QSoundEffect недоступен, используем альтернативу
            self.trade_sound = None
    
    def play_trade_sound(self):
        """Воспроизведение звука при открытии сделки"""
        if self.trade_sound:
            try:
                self.trade_sound.play()
            except:
                # Альтернативный способ уведомления
                print("🔔 Открытие сделки!")
        else:
            print("🔔 Открытие сделки!")
    
    def init_ui(self):
        self.setWindowTitle('Futures Scout - Локальный ИИ-ассистент')
        self.setGeometry(100, 100, 1400, 900)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной слой
        main_layout = QHBoxLayout(central_widget)
        
        # Левая панель управления
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Правая часть (график и стакан)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)
        
        # Применяем темную тему
        self.apply_dark_theme()
    
    def create_left_panel(self):
        """Создание левой панели управления"""
        panel = QWidget()
        panel.setFixedWidth(300)
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title_label = QLabel('Futures Scout')
        title_label.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title_label.setStyleSheet('color: #4a90e2; padding: 10px;')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Блок PnL
        pnl_frame = QFrame()
        pnl_frame.setFrameStyle(QFrame.Shape.Box)
        pnl_frame.setStyleSheet('background-color: rgba(30, 30, 60, 180); border: 1px solid #3a3a6a; border-radius: 5px;')
        pnl_layout = QVBoxLayout(pnl_frame)
        
        pnl_title = QLabel('PnL (Прибыль/Убыток)')
        pnl_title.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        pnl_title.setStyleSheet('color: #4a90e2;')
        pnl_layout.addWidget(pnl_title)
        
        self.pnl_label = QLabel(f'Текущий PnL: ${self.current_pnl:.2f}\nОбщий PnL: ${self.total_pnl:.2f}')
        self.pnl_label.setStyleSheet('color: #ffffff; font-family: monospace;')
        self.pnl_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pnl_layout.addWidget(self.pnl_label)
        
        layout.addWidget(pnl_frame)
        
        # Баланс (только в реальном режиме)
        if self.real_mode:
            balance_label = QLabel('Баланс:')
            balance_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
            layout.addWidget(balance_label)
            
            self.balance_text = QTextEdit()
            self.balance_text.setMaximumHeight(80)
            self.balance_text.setReadOnly(True)
            layout.addWidget(self.balance_text)
        else:
            demo_label = QLabel('ДЕМО-РЕЖИМ\nНИКАКИХ РЕАЛЬНЫХ СДЕЛОК')
            demo_label.setStyleSheet('background-color: rgba(255, 165, 0, 150); color: black; font-weight: bold; padding: 10px; border-radius: 5px;')
            demo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(demo_label)
        
        # Выбор пары
        symbol_layout = QHBoxLayout()
        symbol_label = QLabel('Пара:')
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems([
            'BTC-USDT', 'ETH-USDT', 'BNB-USDT', 'XRP-USDT', 
            'ADA-USDT', 'SOL-USDT', 'DOT-USDT', 'LINK-USDT'
        ])
        self.symbol_combo.setCurrentText(self.current_symbol)
        self.symbol_combo.currentTextChanged.connect(self.on_symbol_changed)
        
        symbol_layout.addWidget(symbol_label)
        symbol_layout.addWidget(self.symbol_combo)
        layout.addLayout(symbol_layout)
        
        # Переключатель режима
        mode_layout = QHBoxLayout()
        mode_label = QLabel('Режим:')
        self.mode_checkbox = QCheckBox('Real / Demo')
        self.mode_checkbox.setChecked(self.real_mode)
        self.mode_checkbox.setEnabled(False)  # Не меняем режим из основного окна
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_checkbox)
        layout.addLayout(mode_layout)
        
        # Кнопка запуска ИИ-агента
        self.ai_button = QPushButton('🤖 Запустить ИИ-агент')
        self.ai_button.clicked.connect(self.on_ai_agent_clicked)
        layout.addWidget(self.ai_button)
        
        # Область для отображения сигналов
        signals_label = QLabel('Сигналы ИИ:')
        signals_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        layout.addWidget(signals_label)
        
        self.signals_area = QTextEdit()
        self.signals_area.setMaximumHeight(200)
        self.signals_area.setReadOnly(True)
        layout.addWidget(self.signals_area)
        
        # Кнопка статистики ИИ
        self.stats_button = QPushButton('📊 Статистика ИИ')
        self.stats_button.clicked.connect(self.show_ai_stats)
        layout.addWidget(self.stats_button)
        
        # Растягиваем пустое пространство вниз
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self):
        """Создание правой панели (график и стакан)"""
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # График
        self.chart_widget = ChartWidget(self.api, self.current_symbol)
        splitter.addWidget(self.chart_widget)
        
        # Стакан ордеров
        self.orderbook_widget = OrderBookWidget(self.api, self.current_symbol)
        splitter.addWidget(self.orderbook_widget)
        
        # Устанавливаем соотношение размеров
        splitter.setSizes([900, 300])
        
        return splitter
    
    def setup_timers(self):
        """Настройка таймеров для обновления данных"""
        # Таймер обновления баланса (только в реальном режиме)
        if self.real_mode:
            self.balance_timer = QTimer()
            self.balance_timer.timeout.connect(self.update_balance)
            self.balance_timer.start(30000)  # Обновление каждые 30 секунд
        
        # Таймер обновления графика
        self.chart_timer = QTimer()
        self.chart_timer.timeout.connect(self.update_chart)
        self.chart_timer.start(10000)  # Обновление каждые 10 секунд
        
        # Таймер обновления стакана
        self.orderbook_timer = QTimer()
        self.orderbook_timer.timeout.connect(self.update_orderbook)
        self.orderbook_timer.start(2000)  # Обновление каждые 2 секунды
        
        # Таймер проверки сигналов ИИ
        self.ai_timer = QTimer()
        self.ai_timer.timeout.connect(self.check_ai_signals)
        self.ai_timer.start(30000)  # Проверка каждые 30 секунд
        
        # Таймер переобучения ИИ (раз в час)
        self.retrain_timer = QTimer()
        self.retrain_timer.timeout.connect(self.retrain_ai_model)
        self.retrain_timer.start(3600000)  # 1 час
        
        # Таймер проверки позиций и PnL (каждые 5 секунд)
        self.pnl_timer = QTimer()
        self.pnl_timer.timeout.connect(self.update_pnl_display)
        self.pnl_timer.start(5000)  # Обновление PnL каждые 5 секунд
    
    def apply_dark_theme(self):
        """Применение темной темы с мягким черным и синим градиентом"""
        dark_style = """
            QMainWindow {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                                                stop: 0 #000000, stop: 1 #0a0a2a);
            }
            QWidget {
                background-color: transparent;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Arial', sans-serif;
            }
            QPushButton {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                                stop: 0 #1a1a3a, stop: 1 #0d0d2d);
                border: 1px solid #3a3a6a;
                padding: 8px;
                border-radius: 5px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                                stop: 0 #2a2a5a, stop: 1 #1d1d4d);
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                                stop: 0 #0d0d2d, stop: 1 #1a1a3a);
            }
            QComboBox {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                                stop: 0 #1a1a3a, stop: 1 #0d0d2d);
                border: 1px solid #3a3a6a;
                padding: 5px;
                color: #ffffff;
                border-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e3e;
                color: #ffffff;
                selection-background-color: #2a2a5a;
            }
            QTextEdit {
                background-color: rgba(10, 10, 30, 180);
                border: 1px solid #3a3a6a;
                color: #ffffff;
                border-radius: 3px;
            }
            QCheckBox {
                spacing: 5px;
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                background-color: #1a1a3a;
                border: 1px solid #3a3a6a;
                border-radius: 2px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #1a1a3a;
            }
            QCheckBox::indicator:checked {
                background-color: #4a4a8a;
            }
            QFrame {
                border: 1px solid #3a3a6a;
                border-radius: 5px;
            }
        """
        self.setStyleSheet(dark_style)
    
    def update_balance(self):
        """Обновление баланса (только в реальном режиме)"""
        if self.real_mode:
            try:
                balance_data = self.api.get_balance()
                if balance_data and 'data' in balance_data:
                    balances = balance_data['data']['balances']
                    balance_text = ''
                    for asset_balance in balances:
                        asset = asset_balance['asset']
                        balance = asset_balance['walletBalance']
                        unrealized = asset_balance['unrealizedProfit']
                        margin_balance = asset_balance.get('marginBalance', balance)
                        balance_text += f"{asset}: {balance} (PNL: {unrealized})\n"
                    self.balance_text.setPlainText(balance_text)
                
                # Обновляем PnL дисплей
                self.update_pnl_display()
            except Exception as e:
                print(f"Ошибка обновления баланса: {e}")
    
    def update_chart(self):
        """Обновление графика"""
        self.chart_widget.update_chart(self.current_symbol)
    
    def update_orderbook(self):
        """Обновление стакана ордеров"""
        self.orderbook_widget.update_orderbook(self.current_symbol)
    
    def on_symbol_changed(self, symbol):
        """Обработка изменения выбранной пары"""
        self.current_symbol = symbol
        self.chart_widget.update_symbol(symbol)
        self.orderbook_widget.update_symbol(symbol)
    
    def on_ai_agent_clicked(self):
        """Обработка нажатия кнопки ИИ-агента"""
        signal = self.ai_agent.generate_signal(self.current_symbol)
        if signal:
            self.display_signal(signal)
            # Воспроизводим звук при генерации сигнала
            self.play_trade_sound()
        else:
            self.signals_area.append("Нет подходящих сигналов для данной пары")
    
    def display_signal(self, signal):
        """Отображение сигнала в интерфейсе"""
        signal_text = (
            f"🔔 [ 🤖 СИГНАЛ: {signal['side']} ]\n"
            f"Монета: {signal['coin']}\n"
            f"Цена входа: ${signal['entry_price']:.2f}\n"
            f"TP: ${signal['tp_price']:.2f} | SL: ${signal['sl_price']:.2f}\n"
            f"R/R: 1:{signal['rr_ratio']:.1f}\n"
            f"Вероятность успеха (ИИ): {signal['confidence']*100:.0f}%\n"
        )
        
        self.signals_area.clear()
        self.signals_area.append(signal_text)
        
        # Обновляем PnL при отображении сигнала
        self.update_pnl_display()
    
    def update_pnl_display(self):
        """Обновление отображения PnL"""
        try:
            # Получаем текущие позиции для расчета PnL
            positions = self.api.get_positions()
            if positions and 'data' in positions:
                total_unrealized_pnl = 0
                for position in positions['data']:
                    if 'unrealizedProfit' in position:
                        total_unrealized_pnl += float(position['unrealizedProfit'])
                
                self.current_pnl = total_unrealized_pnl
                
                # Обновляем отображение PnL
                self.pnl_label.setText(f'Текущий PnL: ${self.current_pnl:.2f}\nОбщий PnL: ${self.total_pnl:.2f}')
                
                # Меняем цвет в зависимости от значения PnL
                if self.current_pnl > 0:
                    self.pnl_label.setStyleSheet('color: #00ff00; font-family: monospace;')  # Зеленый
                elif self.current_pnl < 0:
                    self.pnl_label.setStyleSheet('color: #ff4444; font-family: monospace;')  # Красный
                else:
                    self.pnl_label.setStyleSheet('color: #ffffff; font-family: monospace;')  # Белый
                
        except Exception as e:
            print(f"Ошибка обновления PnL: {e}")
    
    def check_ai_signals(self):
        """Проверка наличия новых сигналов от ИИ"""
        # В реальном приложении здесь будет проверка на новые сигналы
        # и отображение их в интерфейсе
        # Обновляем PnL при проверке сигналов
        self.update_pnl_display()
    
    def retrain_ai_model(self):
        """Переобучение ИИ-модели"""
        if self.ai_agent.should_retrain():
            try:
                self.ai_agent.train_model()
                print("Модель ИИ успешно переобучена")
            except Exception as e:
                print(f"Ошибка переобучения модели ИИ: {e}")
    
    def show_ai_stats(self):
        """Отображение статистики по эффективности ИИ"""
        stats = self.ai_agent.get_performance_stats()
        
        stats_text = (
            f"Статистика ИИ-модели:\n"
            f"Всего сигналов: {stats['total_signals']}\n"
            f"Успешных: {stats['successful_signals']}\n"
            f"Процент успеха: {stats['win_rate']*100:.1f}%\n"
            f"Средняя уверенность (успех): {stats['avg_confidence_success']:.2f}\n"
            f"Средняя уверенность (провал): {stats['avg_confidence_failure']:.2f}\n"
        )
        
        # Показываем в signals_area
        self.signals_area.clear()
        self.signals_area.append(stats_text)