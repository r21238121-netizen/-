"""
Виджет для отображения графика с помощью QWebEngineView и Lightweight Charts
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QTimer
import json


class ChartWidget(QWidget):
    def __init__(self, api, symbol):
        super().__init__()
        self.api = api
        self.symbol = symbol
        self.timeframe = '15m'  # Таймфрейм по умолчанию
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Создаем веб-виджет для отображения графика
        self.web_view = QWebEngineView()
        
        # Загружаем HTML с графиком
        self.load_chart_html()
        
        layout.addWidget(self.web_view)
        self.setLayout(layout)
    
    def load_chart_html(self):
        """Загрузка HTML с графиком Lightweight Charts"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lightweight Charts Example</title>
            <script src="https://unpkg.com/lightweight-charts@3.8.0/dist/lightweight-charts.standalone.production.js"></script>
            <style>
                body { margin: 0; padding: 0; background-color: #000; }
                #chart-container { width: 100%; height: 100%; }
            </style>
        </head>
        <body>
            <div id="chart-container"></div>
            <script>
                // Инициализация графика
                const chartContainer = document.getElementById('chart-container');
                const chart = LightweightCharts.createChart(chartContainer, {
                    width: chartContainer.clientWidth,
                    height: chartContainer.clientHeight,
                    layout: {
                        backgroundColor: '#000',
                        textColor: '#fff',
                    },
                    grid: {
                        vertLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        horzLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    },
                    timeScale: {
                        timeVisible: true,
                        secondsVisible: false,
                    },
                });
                
                // Создаем серию свечей
                const candleSeries = chart.addCandlestickSeries({
                    upColor: '#26a69a',
                    downColor: '#ef5350',
                    borderDownColor: '#ef5350',
                    borderUpColor: '#26a69a',
                    wickDownColor: '#ef5350',
                    wickUpColor: '#26a69a',
                });
                
                // Добавляем данные (заглушка, будет обновляться через Python)
                const initialData = [];
                for (let i = 0; i < 50; i++) {
                    const time = new Date(Date.now() - (50 - i) * 24 * 60 * 60 * 1000);
                    initialData.push({
                        time: time.toISOString().split('T')[0],
                        open: 100 + Math.random() * 10,
                        high: 105 + Math.random() * 10,
                        low: 95 + Math.random() * 10,
                        close: 100 + Math.random() * 10,
                    });
                }
                
                candleSeries.setData(initialData);
                
                // Обработка изменения размера окна
                window.addEventListener('resize', () => {
                    chart.applyOptions({
                        width: chartContainer.clientWidth,
                        height: chartContainer.clientHeight,
                    });
                });
                
                // Функция для обновления данных графика
                window.updateChartData = function(data) {
                    candleSeries.setData(data);
                };
                
                // Функция для добавления маркеров сигналов
                window.addSignalMarker = function(time, position, color, shape) {
                    // Добавляем маркер на график
                    // position: 'aboveBar', 'belowBar', 'inBar'
                    // shape: 'circle', 'square', 'arrowUp', 'arrowDown'
                    candleSeries.setData([...candleSeries.data(), {
                        time: time,
                        open: 0,
                        high: 0,
                        low: 0,
                        close: 0,
                        marker: {
                            position: position,
                            color: color,
                            shape: shape,
                        }
                    }]);
                };
            </script>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html_content)
    
    def update_chart(self, symbol=None):
        """Обновление данных графика"""
        if symbol:
            self.symbol = symbol
        
        try:
            # Получаем исторические данные
            kline_data = self.api.get_kline_data(self.symbol, interval=self.timeframe, limit=100)
            
            if 'data' in kline_data:
                chart_data = []
                for kline in kline_data['data']:
                    chart_data.append({
                        'time': self.format_timestamp(kline[0]),  # timestamp
                        'open': float(kline[1]),
                        'high': float(kline[2]),
                        'low': float(kline[3]),
                        'close': float(kline[4])
                    })
                
                # Обновляем график
                js_code = f"""
                window.updateChartData({json.dumps(chart_data)});
                """
                self.web_view.page().runJavaScript(js_code)
        except Exception as e:
            print(f"Ошибка обновления графика: {e}")
    
    def format_timestamp(self, timestamp_ms):
        """Форматирование timestamp в нужный формат для графика"""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime('%Y-%m-%d')
    
    def update_symbol(self, symbol):
        """Обновление символа для графика"""
        self.symbol = symbol
        self.update_chart()