"""
Виджет для отображения графика с помощью matplotlib и matplotlib.backends.backend_agg
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd


class ChartWidget(QWidget):
    def __init__(self, api, symbol):
        super().__init__()
        self.api = api
        self.symbol = symbol
        self.timeframe = '15m'  # Таймфрейм по умолчанию
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Создаем matplotlib figure и canvas
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        
        # Добавляем placeholder текст
        self.placeholder = QLabel("Загрузка графика...")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Обновляем график
        self.update_chart()
    
    def update_chart(self, symbol=None):
        """Обновление данных графика"""
        if symbol:
            self.symbol = symbol
        
        try:
            # Получаем исторические данные
            kline_data = self.api.get_kline_data(self.symbol, interval=self.timeframe, limit=100)
            
            if 'data' in kline_data:
                # Очищаем предыдущий график
                self.figure.clear()
                
                # Создаем subplot
                ax = self.figure.add_subplot(111)
                
                # Извлекаем данные свечей
                timestamps = []
                opens = []
                highs = []
                lows = []
                closes = []
                
                for kline in kline_data['data']:
                    timestamps.append(kline[0])  # timestamp
                    opens.append(float(kline[1]))
                    highs.append(float(kline[2]))
                    lows.append(float(kline[3]))
                    closes.append(float(kline[4]))
                
                # Преобразуем timestamps в индексы для оси X
                x = range(len(timestamps))
                
                # Рисуем свечи (упрощенно - как столбцы)
                colors = ['green' if close >= open else 'red' for close, open in zip(closes, opens)]
                
                # Рисуем тени (диапазон между high и low)
                for i, (high, low) in enumerate(zip(highs, lows)):
                    ax.plot([i, i], [low, high], color='black', linewidth=0.5)
                
                # Рисуем тело свечи (между open и close)
                for i, (open_price, close_price) in enumerate(zip(opens, closes)):
                    color = 'green' if close_price >= open_price else 'red'
                    height = abs(close_price - open_price)
                    bottom = min(open_price, close_price)
                    
                    # Рисуем прямоугольник для тела свечи
                    ax.bar(i, height, bottom=bottom, width=0.6, color=color, edgecolor='black', linewidth=0.3)
                
                ax.set_title(f'График {self.symbol}')
                ax.set_xlabel('Время')
                ax.set_ylabel('Цена')
                
                # Поворачиваем метки на оси X для лучшего отображения
                ax.tick_params(axis='x', rotation=45)
                
                # Обновляем canvas
                self.figure.tight_layout()
                self.canvas.draw()
            else:
                # Если данных нет, показываем сообщение
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.text(0.5, 0.5, 'Нет данных для отображения', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=14)
                ax.set_title(f'График {self.symbol}')
                self.canvas.draw()
                
        except Exception as e:
            print(f"Ошибка обновления графика: {e}")
            # Показываем сообщение об ошибке
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Ошибка загрузки данных: {str(e)}', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14)
            ax.set_title(f'График {self.symbol}')
            self.canvas.draw()
    
    def format_timestamp(self, timestamp_ms):
        """Форматирование timestamp в нужный формат для графика"""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime('%Y-%m-%d')
    
    def update_symbol(self, symbol):
        """Обновление символа для графика"""
        self.symbol = symbol
        self.update_chart()
    

