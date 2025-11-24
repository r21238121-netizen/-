"""
Модуль ИИ-агента для анализа рынка и генерации сигналов
"""
import pandas as pd
import numpy as np
import xgboost as xgb
from datetime import datetime, timedelta
import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pickle
import requests  # Для получения данных с публичных источников


Base = declarative_base()


class SignalHistory(Base):
    __tablename__ = 'signals_history'
    
    id = Column(Integer, primary_key=True)
    coin = Column(String)
    side = Column(String)  # 'LONG' or 'SHORT'
    entry_price = Column(Float)
    tp_price = Column(Float)
    sl_price = Column(Float)
    timestamp = Column(DateTime)
    confidence = Column(Float)  # Вероятность успеха (0-1)
    result = Column(String)  # 'SUCCESS', 'FAILURE', 'PENDING'
    realized_result = Column(Boolean)  # Успешно ли сработал сигнал
    close_timestamp = Column(DateTime)  # Время закрытия
    close_price = Column(Float)  # Цена закрытия


class AIAgent:
    def __init__(self, api, demo_mode=False):
        self.api = api
        self.demo_mode = demo_mode
        
        # Настройка базы данных для хранения истории сигналов
        db_path = os.path.join(os.path.expanduser("~"), ".futures_scout", "signals_history.db")
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Путь к модели
        self.model_path = os.path.join(os.path.expanduser("~"), ".futures_scout", "ai_model.pkl")
        
        # Загружаем или создаем модель
        self.model = self._load_model()
        
        # Таймер для переобучения (раз в 24 часа)
        self.last_training_time = datetime.now() - timedelta(days=1)
    
    def _load_model(self):
        """Загрузка сохраненной модели или создание новой"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                return pickle.load(f)
        else:
            # Создаем новую модель
            return xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
    
    def _save_model(self):
        """Сохранение модели"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
    
    def generate_signal(self, symbol):
        """Генерация торгового сигнала для указанной монеты"""
        try:
            # Получаем рыночные данные из BingX (торговые функции)
            kline_data = self.api.get_kline_data(symbol, interval='15m', limit=50)
            price_data = self.api.get_market_price(symbol)
            orderbook = self.api.get_orderbook(symbol)
            oi_data = self.api.get_open_interest(symbol)
            funding_data = self.api.get_funding_rate(symbol)
            
            # Получаем дополнительные данные с публичных источников (для графиков и анализа)
            external_market_data = self._get_external_market_data(symbol)
            
            # Обрабатываем данные и генерируем признаки
            features = self._extract_features(kline_data, price_data, orderbook, oi_data, funding_data, external_market_data)
            
            # Получаем вероятность успеха от модели
            confidence = self._predict_success_probability(features)
            
            # Простая стратегия на основе технического анализа
            signal = self._technical_analysis_signal(kline_data, price_data)
            
            if signal is not None and confidence > 0.6:  # Порог для сигнала
                # Рассчитываем точки входа
                current_price = float(price_data['data'][0]['price'])
                
                # Рассчитываем TP и SL на основе ATR или волатильности
                atr = self._calculate_atr(kline_data)
                tp_distance = atr * 2  # 2 ATR для TP
                sl_distance = atr * 1  # 1 ATR для SL
                
                if signal == 'LONG':
                    entry_price = current_price
                    tp_price = current_price + tp_distance
                    sl_price = current_price - sl_distance
                else:  # SHORT
                    entry_price = current_price
                    tp_price = current_price - tp_distance
                    sl_price = current_price + sl_distance
                
                # Сохраняем сигнал в историю
                signal_obj = SignalHistory(
                    coin=symbol,
                    side=signal,
                    entry_price=entry_price,
                    tp_price=tp_price,
                    sl_price=sl_price,
                    timestamp=datetime.now(),
                    confidence=confidence,
                    result='PENDING'
                )
                
                self.session.add(signal_obj)
                self.session.commit()
                
                return {
                    'coin': symbol,
                    'side': signal,
                    'entry_price': entry_price,
                    'tp_price': tp_price,
                    'sl_price': sl_price,
                    'confidence': confidence,
                    'rr_ratio': abs((tp_price - entry_price) / (sl_price - entry_price)) if signal == 'LONG' else abs((entry_price - tp_price) / (entry_price - sl_price))
                }
        
        except Exception as e:
            print(f"Ошибка при генерации сигнала: {e}")
        
        return None
    
    def _get_external_market_data(self, symbol):
        """Получение данных с публичных источников (для графиков и анализа)"""
        # Заменяем формат символа для публичных API (например, Binance)
        binance_symbol = symbol.replace('-', '')
        
        try:
            # Получаем данные с Binance API для графиков
            response = requests.get(f"https://api.binance.com/api/v3/klines", 
                                  params={'symbol': binance_symbol, 'interval': '15m', 'limit': 100})
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            print(f"Ошибка при получении внешних данных: {e}")
            return None
    
    def _extract_features(self, kline_data, price_data, orderbook, oi_data, funding_data, external_market_data):
        """Извлечение признаков из рыночных данных"""
        # Извлекаем цены из свечей BingX
        if 'data' in kline_data and len(kline_data['data']) > 0:
            closes = [float(candle[4]) for candle in kline_data['data']]
            opens = [float(candle[1]) for candle in kline_data['data']]
            highs = [float(candle[2]) for candle in kline_data['data']]
            lows = [float(candle[3]) for candle in kline_data['data']]
            volumes = [float(candle[5]) for candle in kline_data['data']]
        else:
            # Возвращаем пустой вектор признаков в случае ошибки
            return np.array([0] * 20)
        
        # Рассчитываем технические индикаторы
        current_price = float(price_data['data'][0]['price']) if price_data.get('data') else closes[-1]
        
        # SMA
        sma_20 = sum(closes[-20:]) / min(20, len(closes)) if len(closes) >= 20 else current_price
        sma_50 = sum(closes[-50:]) / min(50, len(closes)) if len(closes) >= 50 else current_price
        
        # RSI (упрощенный расчет)
        if len(closes) > 14:
            gains = []
            losses = []
            for i in range(1, 15):
                change = closes[-i] - closes[-i-1]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / 14 if gains else 0
            avg_loss = sum(losses) / 14 if losses else 0.001  # Избегаем деления на 0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = 50  # Нейтральное значение
        
        # MACD (упрощенный расчет)
        ema_12 = self._calculate_ema(closes, 12)
        ema_26 = self._calculate_ema(closes, 26)
        macd = ema_12 - ema_26 if ema_12 is not None and ema_26 is not None else 0
        
        # Волатильность (стандартное отклонение)
        volatility = np.std(closes[-20:]) if len(closes) >= 20 else 0
        
        # Volume (последние 5 свечей)
        avg_volume = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else 0
        current_volume = volumes[-1] if volumes else 0
        
        # Orderbook imbalance
        bids_total = sum([float(order[1]) for order in orderbook.get('data', {}).get('bids', [])[:5]])
        asks_total = sum([float(order[1]) for order in orderbook.get('data', {}).get('asks', [])[:5]])
        ob_imbalance = (bids_total - asks_total) / (bids_total + asks_total + 1e-10)  # Избегаем деления на 0
        
        # Open Interest изменение (если доступно)
        oi_change = 0  # Заглушка, в реальности нужно сравнивать с предыдущим значением
        
        # Funding Rate
        funding_rate = float(funding_data['data'][0]['fundingRate']) if funding_data.get('data') and len(funding_data['data']) > 0 else 0
        
        # Временные признаки
        current_time = datetime.now()
        hour = current_time.hour / 24.0  # Нормализуем
        day_of_week = current_time.weekday() / 7.0  # Нормализуем
        
        # Добавляем признаки из внешних данных, если доступны
        external_features = []
        if external_market_data:
            try:
                ext_closes = [float(candle[4]) for candle in external_market_data]
                ext_volatility = np.std(ext_closes[-20:]) if len(ext_closes) >= 20 else 0
                external_features = [ext_volatility]
            except:
                external_features = [0]
        else:
            external_features = [0]
        
        # Собираем признаки
        features = np.array([
            current_price,
            sma_20,
            sma_50,
            rsi,
            macd,
            volatility,
            avg_volume,
            current_volume,
            ob_imbalance,
            oi_change,
            funding_rate,
            hour,
            day_of_week,
            current_price / sma_20 if sma_20 != 0 else 1,  # Цена относительно SMA20
            current_price / sma_50 if sma_50 != 0 else 1,  # Цена относительно SMA50
            len(closes),  # Количество свечей
            closes[-1] / closes[0] if closes[0] != 0 else 1,  # Изменение цены за период
            sum(volumes),  # Общий объем
            closes[-1] - closes[-2] if len(closes) > 1 else 0,  # Изменение цены за последнюю свечу
            closes[-1] - sum(closes[-5:]) / 5 if len(closes) >= 5 else 0  # Отклонение от средней 5-свечей
        ] + external_features)
        
        return features
    
    def _calculate_ema(self, prices, period):
        """Расчет EMA"""
        if len(prices) < period:
            return None
        
        prices_slice = prices[-period:]
        ema = prices_slice[0]
        multiplier = 2 / (period + 1)
        
        for price in prices_slice[1:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _calculate_atr(self, kline_data):
        """Расчет Average True Range"""
        if 'data' not in kline_data or len(kline_data['data']) < 14:
            return 100  # Значение по умолчанию
        
        true_ranges = []
        data = kline_data['data']
        
        for i in range(1, min(14, len(data))):
            high = float(data[i][2])
            low = float(data[i][3])
            prev_close = float(data[i-1][4])
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        return sum(true_ranges) / len(true_ranges) if true_ranges else 100
    
    def _technical_analysis_signal(self, kline_data, price_data):
        """Генерация сигнала на основе технического анализа"""
        if 'data' not in kline_data or len(kline_data['data']) < 20:
            return None
        
        closes = [float(candle[4]) for candle in kline_data['data']]
        highs = [float(candle[2]) for candle in kline_data['data']]
        lows = [float(candle[3]) for candle in kline_data['data']]
        
        current_price = float(price_data['data'][0]['price']) if price_data.get('data') else closes[-1]
        
        # Простая стратегия: если цена выше 20-периодной MA и RSI в диапазоне 30-70 - LONG
        # если цена ниже 20-периодной MA и RSI в диапазоне 30-70 - SHORT
        if len(closes) >= 20:
            ma_20 = sum(closes[-20:]) / 20
            
            # Упрощенный RSI
            gains = []
            losses = []
            for i in range(1, min(15, len(closes))):
                change = closes[-i] - closes[-i-1]
                if change > 0:
                    gains.append(change)
                else:
                    losses.append(abs(change))
            
            if gains and losses:
                avg_gain = sum(gains) / min(14, len(gains))
                avg_loss = sum(losses) / min(14, len(losses))
                
                if avg_loss != 0:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    
                    if current_price > ma_20 and 30 < rsi < 70:
                        return 'LONG'
                    elif current_price < ma_20 and 30 < rsi < 70:
                        return 'SHORT'
        
        return None
    
    def _predict_success_probability(self, features):
        """Предсказание вероятности успеха сигнала"""
        try:
            # Временно возвращаем случайное значение, пока не обучим модель
            # В реальности здесь будет вызов модели
            if hasattr(self.model, 'predict_proba'):
                # Если модель поддерживает вероятности
                proba = self.model.predict_proba(features.reshape(1, -1))
                # Возвращаем вероятность класса 1 (успех)
                return proba[0][1] if proba.shape[1] > 1 else 0.5
            else:
                # Если модель не поддерживает вероятности, возвращаем 0.5
                return 0.5
        except:
            # В случае ошибки возвращаем среднюю вероятность
            return 0.5
    
    def update_signal_result(self, signal_id, result, close_price=None, close_timestamp=None):
        """Обновление результата сигнала после закрытия позиции"""
        signal = self.session.query(SignalHistory).filter(SignalHistory.id == signal_id).first()
        if signal:
            signal.result = 'SUCCESS' if result else 'FAILURE'
            signal.realized_result = result
            signal.close_price = close_price
            signal.close_timestamp = close_timestamp or datetime.now()
            self.session.commit()
    
    def train_model(self):
        """Переобучение модели на основе истории сигналов"""
        # Получаем историю сигналов
        signals = self.session.query(SignalHistory).filter(
            SignalHistory.result.in_(['SUCCESS', 'FAILURE'])
        ).all()
        
        if len(signals) < 10:  # Минимум 10 сигналов для обучения
            return
        
        # Подготовка данных для обучения
        X = []
        y = []
        
        for signal in signals:
            # Здесь нужно восстановить признаки, которые использовались при генерации сигнала
            # В реальности это требует хранения признаков при генерации
            # Пока используем простые признаки на основе данных сигнала
            features = [
                signal.entry_price or 0,
                signal.tp_price or 0,
                signal.sl_price or 0,
                signal.confidence or 0,
                1 if signal.side == 'LONG' else 0,  # one-hot для side
                0 if signal.side == 'LONG' else 1   # one-hot для side
            ]
            X.append(features)
            y.append(1 if signal.result == 'SUCCESS' else 0)  # 1 - успех, 0 - провал
        
        if len(X) > 0:
            X = np.array(X)
            y = np.array(y)
            
            # Обучаем модель
            self.model.fit(X, y)
            
            # Сохраняем модель
            self._save_model()
            
            # Обновляем время последнего обучения
            self.last_training_time = datetime.now()
    
    def should_retrain(self):
        """Проверка необходимости переобучения модели"""
        return (datetime.now() - self.last_training_time).days >= 1  # Ежедневное переобучение
    
    def get_performance_stats(self):
        """Получение статистики по эффективности ИИ"""
        all_signals = self.session.query(SignalHistory).filter(
            SignalHistory.result.in_(['SUCCESS', 'FAILURE'])
        ).count()
        
        successful_signals = self.session.query(SignalHistory).filter(
            SignalHistory.result == 'SUCCESS'
        ).count()
        
        win_rate = successful_signals / all_signals if all_signals > 0 else 0
        
        # Средняя уверенность успешных сигналов
        avg_confidence_success = self.session.query(SignalHistory).filter(
            SignalHistory.result == 'SUCCESS'
        ).with_entities(SignalHistory.confidence).all()
        
        avg_conf_success = np.mean([c.confidence for c in avg_confidence_success]) if avg_confidence_success else 0
        
        # Средняя уверенность неуспешных сигналов
        avg_confidence_failure = self.session.query(SignalHistory).filter(
            SignalHistory.result == 'FAILURE'
        ).with_entities(SignalHistory.confidence).all()
        
        avg_conf_failure = np.mean([c.confidence for c in avg_confidence_failure]) if avg_confidence_failure else 0
        
        return {
            'total_signals': all_signals,
            'successful_signals': successful_signals,
            'win_rate': win_rate,
            'avg_confidence_success': avg_conf_success,
            'avg_confidence_failure': avg_conf_failure
        }
    
    def analyze_market_situation(self, symbol):
        """Анализ текущей рыночной ситуации и генерация устного отчета"""
        try:
            # Получаем данные
            kline_data = self.api.get_kline_data(symbol, interval='1h', limit=50)
            price_data = self.api.get_market_price(symbol)
            orderbook = self.api.get_orderbook(symbol)
            
            if 'data' not in kline_data or len(kline_data['data']) < 20:
                return f"Недостаточно данных для анализа {symbol}"
            
            closes = [float(candle[4]) for candle in kline_data['data']]
            highs = [float(candle[2]) for candle in kline_data['data']]
            lows = [float(candle[3]) for candle in kline_data['data']]
            
            current_price = float(price_data['data'][0]['price']) if price_data.get('data') else closes[-1]
            
            # Рассчитываем индикаторы
            sma_20 = sum(closes[-20:]) / 20
            sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sma_20
            price_change_24h = ((closes[-1] - closes[0]) / closes[0]) * 100 if len(closes) > 0 else 0
            
            # Определяем тренд
            if current_price > sma_20 and sma_20 > sma_50:
                trend = "восходящий"
            elif current_price < sma_20 and sma_20 < sma_50:
                trend = "нисходящий"
            else:
                trend = "боковой"
            
            # Определяем ликвидность по стакану
            bids_total = sum([float(order[1]) for order in orderbook.get('data', {}).get('bids', [])[:10]])
            asks_total = sum([float(order[1]) for order in orderbook.get('data', {}).get('asks', [])[:10]])
            liquidity_ratio = bids_total / (asks_total + 1e-10)
            
            if liquidity_ratio > 1.2:
                liquidity = "высокая"
            elif liquidity_ratio < 0.8:
                liquidity = "низкая"
            else:
                liquidity = "средняя"
            
            # Генерируем устный анализ
            analysis = f"""
            Анализ рынка для {symbol}:
            - Текущая цена: {current_price:.4f} USDT
            - 24-часовое изменение: {price_change_24h:+.2f}%
            - Тренд: {trend}
            - Уровень ликвидности: {liquidity}
            
            Технический анализ:
            - Цена находится {'выше' if current_price > sma_20 else 'ниже'} 20-периодной скользящей средней
            - SMA20: {sma_20:.4f}, SMA50: {sma_50:.4f}
            
            Рекомендация: {'Трендовый рост возможен' if trend == 'восходящий' else 'Возможен откат' if trend == 'нисходящий' else 'Неопределенная ситуация'}
            """
            
            return analysis.strip()
            
        except Exception as e:
            return f"Ошибка при анализе рынка {symbol}: {str(e)}"
    
    def speak_analysis(self, symbol):
        """Функция для озвучивания анализа (возвращает текст для синтеза речи)"""
        analysis = self.analyze_market_situation(symbol)
        return analysis