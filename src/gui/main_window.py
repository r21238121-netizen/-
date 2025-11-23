"""
Основное окно приложения
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QComboBox, QCheckBox, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
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
        
        self.init_ui()
        self.setup_timers()
    
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
            demo_label.setStyleSheet('background-color: orange; color: black; font-weight: bold; padding: 10px;')
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
        self.ai_button = QPushButton('Запустить ИИ-агент')
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
        self.stats_button = QPushButton('Статистика ИИ')
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
    
    def apply_dark_theme(self):
        """Применение темной темы"""
        dark_style = """
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3c3f41;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #4c4f51;
            }
            QPushButton:pressed {
                background-color: #5c5f61;
            }
            QComboBox {
                background-color: #3c3f41;
                border: 1px solid #555555;
                padding: 5px;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            QCheckBox::indicator:unchecked {
                image: url(/tmp/checkbox_unchecked.png);
            }
            QCheckBox::indicator:checked {
                image: url(/tmp/checkbox_checked.png);
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
                        balance_text += f"{asset}: {balance} (PNL: {unrealized})\n"
                    self.balance_text.setPlainText(balance_text)
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
        else:
            self.signals_area.append("Нет подходящих сигналов для данной пары")
    
    def display_signal(self, signal):
        """Отображение сигнала в интерфейсе"""
        signal_text = (
            f"[ 🤖 СИГНАЛ: {signal['side']} ]\n"
            f"Монета: {signal['coin']}\n"
            f"Цена входа: ${signal['entry_price']:.2f}\n"
            f"TP: ${signal['tp_price']:.2f} | SL: ${signal['sl_price']:.2f}\n"
            f"R/R: 1:{signal['rr_ratio']:.1f}\n"
            f"Вероятность успеха (ИИ): {signal['confidence']*100:.0f}%\n"
        )
        
        self.signals_area.clear()
        self.signals_area.append(signal_text)
    
    def check_ai_signals(self):
        """Проверка наличия новых сигналов от ИИ"""
        # В реальном приложении здесь будет проверка на новые сигналы
        # и отображение их в интерфейсе
        pass
    
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