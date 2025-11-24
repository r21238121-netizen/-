"""
Виджет для отображения стакана ордеров
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtMultimedia import QSoundEffect  # Для звуковых уведомлений
import os


class OrderBookWidget(QWidget):
    def __init__(self, api, symbol):
        super().__init__()
        self.api = api
        self.symbol = symbol
        
        # Инициализация звуковых эффектов
        self.init_sound_effects()
        
        self.init_ui()
    
    def init_sound_effects(self):
        """Инициализация звуковых эффектов"""
        try:
            # Создаем директорию для звуков если не существует
            sound_dir = os.path.join(os.path.expanduser("~"), ".futures_scout", "sounds")
            os.makedirs(sound_dir, exist_ok=True)
            
            # Создаем простой звуковой файл для уведомлений (в реальном приложении можно использовать реальные звуки)
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
        layout = QVBoxLayout(self)
        
        # Заголовок
        title_label = QLabel('Стакан ордеров')
        title_label.setStyleSheet('font-weight: bold; font-size: 14px;')
        layout.addWidget(title_label)
        
        # Таблица стакана
        self.orderbook_table = QTableWidget()
        self.orderbook_table.setColumnCount(2)
        self.orderbook_table.setHorizontalHeaderLabels(['Цена', 'Количество'])
        
        # Настройка таблицы
        header = self.orderbook_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.orderbook_table)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.buy_button = QPushButton('Купить по лучшему')
        self.buy_button.clicked.connect(self.on_buy_clicked)
        button_layout.addWidget(self.buy_button)
        
        self.sell_button = QPushButton('Продать по лучшему')
        self.sell_button.clicked.connect(self.on_sell_clicked)
        button_layout.addWidget(self.sell_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_orderbook(self, symbol=None):
        """Обновление стакана ордеров"""
        if symbol:
            self.symbol = symbol
        
        try:
            orderbook_data = self.api.get_orderbook(self.symbol, limit=10)
            
            if 'data' in orderbook_data:
                bids = orderbook_data['data'].get('bids', [])
                asks = orderbook_data['data'].get('asks', [])
                
                # Очищаем таблицу
                self.orderbook_table.setRowCount(len(bids) + len(asks))
                
                # Добавляем биды (покупка) - отсортированы от highest к lowest
                for i, bid in enumerate(bids):
                    price = float(bid[0])
                    amount = float(bid[1])
                    
                    # Цена
                    price_item = QTableWidgetItem(f'{price:.2f}')
                    price_item.setTextAlignment(0x0084)  # AlignRight
                    price_item.setBackground(QColor(0, 100, 0))  # Dark green
                    price_item.setForeground(QColor(255, 255, 255))  # White text
                    self.orderbook_table.setItem(i, 0, price_item)
                    
                    # Количество
                    amount_item = QTableWidgetItem(f'{amount:.4f}')
                    amount_item.setTextAlignment(0x0084)  # AlignRight
                    amount_item.setBackground(QColor(0, 100, 0))  # Dark green
                    amount_item.setForeground(QColor(255, 255, 255))  # White text
                    self.orderbook_table.setItem(i, 1, amount_item)
                
                # Добавляем аски (продажа) - отсортированы от lowest к highest
                for i, ask in enumerate(asks):
                    idx = len(bids) + i
                    price = float(ask[0])
                    amount = float(ask[1])
                    
                    # Цена
                    price_item = QTableWidgetItem(f'{price:.2f}')
                    price_item.setTextAlignment(0x0084)  # AlignRight
                    price_item.setBackground(QColor(139, 0, 0))  # Dark red
                    price_item.setForeground(QColor(255, 255, 255))  # White text
                    self.orderbook_table.setItem(idx, 0, price_item)
                    
                    # Количество
                    amount_item = QTableWidgetItem(f'{amount:.4f}')
                    amount_item.setTextAlignment(0x0084)  # AlignRight
                    amount_item.setBackground(QColor(139, 0, 0))  # Dark red
                    amount_item.setForeground(QColor(255, 255, 255))  # White text
                    self.orderbook_table.setItem(idx, 1, amount_item)
        except Exception as e:
            print(f"Ошибка обновления стакана: {e}")
    
    def update_symbol(self, symbol):
        """Обновление символа для стакана"""
        self.symbol = symbol
    
    def on_buy_clicked(self):
        """Обработка нажатия кнопки покупки"""
        try:
            # Получаем лучшую цену продажи (первый ask)
            orderbook_data = self.api.get_orderbook(self.symbol, limit=1)
            if 'data' in orderbook_data and orderbook_data['data'].get('asks'):
                best_ask_price = float(orderbook_data['data']['asks'][0][0])
                
                # В реальном приложении здесь будет размещение ордера
                # Пока просто выводим сообщение
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, 'Покупка', f'Цена лучшего предложения для покупки: {best_ask_price}')
                
                # Воспроизводим звук при открытии сделки
                self.play_trade_sound()
                
                # В реальном режиме можно было бы разместить ордер:
                # if hasattr(self.api, 'place_order') and not self.api.demo_mode:
                #     result = self.api.place_order(self.symbol, 'BUY', quantity, 'MARKET')
                #     print(f"Ордер размещен: {result}")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при размещении ордера: {e}')
    
    def on_sell_clicked(self):
        """Обработка нажатия кнопки продажи"""
        try:
            # Получаем лучшую цену покупки (первый bid)
            orderbook_data = self.api.get_orderbook(self.symbol, limit=1)
            if 'data' in orderbook_data and orderbook_data['data'].get('bids'):
                best_bid_price = float(orderbook_data['data']['bids'][0][0])
                
                # В реальном приложении здесь будет размещение ордера
                # Пока просто выводим сообщение
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, 'Продажа', f'Цена лучшего предложения для продажи: {best_bid_price}')
                
                # Воспроизводим звук при открытии сделки
                self.play_trade_sound()
                
                # В реальном режиме можно было бы разместить ордер:
                # if hasattr(self.api, 'place_order') and not self.api.demo_mode:
                #     result = self.api.place_order(self.symbol, 'SELL', quantity, 'MARKET')
                #     print(f"Ордер размещен: {result}")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при размещении ордера: {e}')


