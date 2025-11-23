import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import talib

class TechnicalAnalysis:
    def __init__(self):
        pass

    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """Расчет RSI индикатора"""
        prices = np.array(prices)
        rsi = talib.RSI(prices, timeperiod=period)
        return rsi.tolist()

    def calculate_macd(self, prices: List[float]) -> Tuple[List[float], List[float], List[float]]:
        """Расчет MACD индикатора"""
        prices = np.array(prices)
        macd, macdsignal, macdhist = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)
        return macd.tolist(), macdsignal.tolist(), macdhist.tolist()

    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std: int = 2) -> Tuple[List[float], List[float], List[float]]:
        """Расчет полос Боллинджера"""
        prices = np.array(prices)
        upper, middle, lower = talib.BBANDS(prices, timeperiod=period, nbdevup=std, nbdevdn=std, matype=0)
        return upper.tolist(), middle.tolist(), lower.tolist()

    def calculate_stochastic(self, highs: List[float], lows: List[float], closes: List[float], k_period: int = 14, d_period: int = 3) -> Tuple[List[float], List[float]]:
        """Расчет стохастического осциллятора"""
        highs = np.array(highs)
        lows = np.array(lows)
        closes = np.array(closes)
        slowk, slowd = talib.STOCH(highs, lows, closes, fastk_period=k_period, slowk_period=d_period, slowd_period=d_period)
        return slowk.tolist(), slowd.tolist()

    def calculate_sma(self, prices: List[float], period: int = 20) -> List[float]:
        """Расчет простой скользящей средней"""
        prices = np.array(prices)
        sma = talib.SMA(prices, timeperiod=period)
        return sma.tolist()

    def calculate_ema(self, prices: List[float], period: int = 20) -> List[float]:
        """Расчет экспоненциальной скользящей средней"""
        prices = np.array(prices)
        ema = talib.EMA(prices, timeperiod=period)
        return ema.tolist()

    def calculate_support_resistance(self, highs: List[float], lows: List[float], window: int = 10) -> Tuple[float, float]:
        """Расчет уровней поддержки и сопротивления"""
        highs = np.array(highs)
        lows = np.array(lows)
        
        # Находим локальные максимумы и минимумы
        resistance = np.max(highs[-window:])
        support = np.min(lows[-window:])
        
        return support, resistance

    def analyze_trend(self, prices: List[float]) -> str:
        """Анализ тренда"""
        if len(prices) < 50:
            return "insufficient_data"
        
        # Рассчитываем 20-периодную и 50-периодную EMA
        ema_short = self.calculate_ema(prices, 20)
        ema_long = self.calculate_ema(prices, 50)
        
        if ema_short[-1] > ema_long[-1] and ema_short[-2] <= ema_long[-2]:
            return "bullish"
        elif ema_short[-1] < ema_long[-1] and ema_short[-2] >= ema_long[-2]:
            return "bearish"
        elif ema_short[-1] > ema_long[-1]:
            return "uptrend"
        elif ema_short[-1] < ema_long[-1]:
            return "downtrend"
        else:
            return "sideways"

    def generate_signal(self, current_price: float, rsi: float, macd_hist: float, bb_position: float, stochastic_k: float, stochastic_d: float, trend: str) -> Dict:
        """Генерация торгового сигнала на основе всех индикаторов"""
        signal = {
            "action": "HOLD",  # BUY, SELL, HOLD
            "confidence": 0.0,
            "reasons": []
        }
        
        # RSI сигналы
        if rsi < 30:  # Перепроданность
            signal["action"] = "BUY"
            signal["confidence"] += 0.2
            signal["reasons"].append("RSI: перепроданность")
        elif rsi > 70:  # Перекупленность
            signal["action"] = "SELL"
            signal["confidence"] += 0.2
            signal["reasons"].append("RSI: перекупленность")
        
        # MACD сигналы
        if macd_hist > 0 and macd_hist > macd_hist:  # Бычий кросс
            if signal["action"] == "BUY":
                signal["confidence"] += 0.2
            else:
                signal["action"] = "BUY"
            signal["reasons"].append("MACD: бычий сигнал")
        elif macd_hist < 0 and macd_hist < macd_hist:  # Медвежий кросс
            if signal["action"] == "SELL":
                signal["confidence"] += 0.2
            else:
                signal["action"] = "SELL"
            signal["reasons"].append("MACD: медвежий сигнал")
        
        # Полосы Боллинджера
        if bb_position < 0.1:  # Цена около нижней полосы (перепродано)
            if signal["action"] == "BUY":
                signal["confidence"] += 0.15
            else:
                signal["action"] = "BUY"
            signal["reasons"].append("BB: цена около нижней полосы")
        elif bb_position > 0.9:  # Цена около верхней полосы (перекуплено)
            if signal["action"] == "SELL":
                signal["confidence"] += 0.15
            else:
                signal["action"] = "SELL"
            signal["reasons"].append("BB: цена около верхней полосы")
        
        # Стохастик
        if stochastic_k < 20 and stochastic_d < 20 and stochastic_k > stochastic_d:  # Перепроданность и бычий кросс
            if signal["action"] == "BUY":
                signal["confidence"] += 0.15
            else:
                signal["action"] = "BUY"
            signal["reasons"].append("Stochastic: бычий сигнал в зоне перепроданности")
        elif stochastic_k > 80 and stochastic_d > 80 and stochastic_k < stochastic_d:  # Перекупленность и медвежий кросс
            if signal["action"] == "SELL":
                signal["confidence"] += 0.15
            else:
                signal["action"] = "SELL"
            signal["reasons"].append("Stochastic: медвежий сигнал в зоне перекупленности")
        
        # Тренд
        if trend == "uptrend" and signal["action"] == "BUY":
            signal["confidence"] += 0.1
            signal["reasons"].append("Trend: восходящий тренд подтверждает покупку")
        elif trend == "downtrend" and signal["action"] == "SELL":
            signal["confidence"] += 0.1
            signal["reasons"].append("Trend: нисходящий тренд подтверждает продажу")
        
        # Ограничиваем уверенность от 0 до 1
        signal["confidence"] = min(1.0, signal["confidence"])
        
        return signal

    def analyze_pair(self, klines_data: List[List], pair: str) -> Dict:
        """Полный анализ торговой пары"""
        # Извлекаем данные
        opens = [float(k[1]) for k in klines_data]
        highs = [float(k[2]) for k in klines_data]
        lows = [float(k[3]) for k in klines_data]
        closes = [float(k[4]) for k in klines_data]
        volumes = [float(k[5]) for k in klines_data]
        
        current_price = closes[-1]
        
        # Рассчитываем индикаторы
        rsi_values = self.calculate_rsi(closes)
        macd_line, macd_signal, macd_hist = self.calculate_macd(closes)
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(closes)
        stoch_k, stoch_d = self.calculate_stochastic(highs, lows, closes)
        trend = self.analyze_trend(closes)
        
        # Определяем позицию цены относительно полос Боллинджера (0-1, где 0 - нижняя полоса, 1 - верхняя)
        bb_position = (current_price - bb_lower[-1]) / (bb_upper[-1] - bb_lower[-1]) if (bb_upper[-1] - bb_lower[-1]) != 0 else 0.5
        
        # Генерируем сигнал
        signal = self.generate_signal(
            current_price=current_price,
            rsi=rsi_values[-1] if rsi_values[-1] is not None else 50,
            macd_hist=macd_hist[-1] if macd_hist[-1] is not None else 0,
            bb_position=bb_position,
            stochastic_k=stoch_k[-1] if stoch_k[-1] is not None else 50,
            stochastic_d=stoch_d[-1] if stoch_d[-1] is not None else 50,
            trend=trend
        )
        
        # Рассчитываем уровни поддержки и сопротивления
        support, resistance = self.calculate_support_resistance(highs, lows)
        
        return {
            "pair": pair,
            "current_price": current_price,
            "indicators": {
                "rsi": rsi_values[-1] if rsi_values[-1] is not None else 50,
                "macd": {
                    "line": macd_line[-1] if macd_line[-1] is not None else 0,
                    "signal": macd_signal[-1] if macd_signal[-1] is not None else 0,
                    "histogram": macd_hist[-1] if macd_hist[-1] is not None else 0
                },
                "bollinger_bands": {
                    "upper": bb_upper[-1] if bb_upper[-1] is not None else current_price,
                    "middle": bb_middle[-1] if bb_middle[-1] is not None else current_price,
                    "lower": bb_lower[-1] if bb_lower[-1] is not None else current_price
                },
                "stochastic": {
                    "k": stoch_k[-1] if stoch_k[-1] is not None else 50,
                    "d": stoch_d[-1] if stoch_d[-1] is not None else 50
                },
                "trend": trend,
                "support": support,
                "resistance": resistance
            },
            "signal": signal
        }

    def rank_pairs(self, pairs_data: Dict[str, Dict]) -> List[Tuple[str, float]]:
        """Ранжирование торговых пар по потенциалу"""
        rankings = []
        
        for pair, data in pairs_data.items():
            score = 0.0
            signal = data.get("signal", {})
            indicators = data.get("indicators", {})
            
            # Оценка на основе сигнала
            if signal.get("action") == "BUY":
                score += signal.get("confidence", 0) * 100
            elif signal.get("action") == "SELL":
                score += signal.get("confidence", 0) * 100
            else:
                score += 0  # HOLD
            
            # Оценка на основе RSI (отклонение от 50)
            rsi = indicators.get("rsi", 50)
            if rsi < 30 or rsi > 70:  # Сильное отклонение - потенциал
                score += 10
            elif 30 <= rsi <= 70:
                score += abs(rsi - 50)  # Чем дальше от 50, тем выше потенциал
            
            # Оценка на основе MACD
            macd_hist = indicators.get("macd", {}).get("histogram", 0)
            score += abs(macd_hist) * 10
            
            # Оценка на основе расстояния до уровней поддержки/сопротивления
            current_price = data.get("current_price", 0)
            support = indicators.get("support", current_price)
            resistance = indicators.get("resistance", current_price)
            
            if current_price > support and current_price < resistance:
                # Цена между поддержкой и сопротивлением
                dist_to_support = abs(current_price - support) / current_price
                dist_to_resistance = abs(resistance - current_price) / current_price
                score += (1 - min(dist_to_support, dist_to_resistance)) * 20
            
            rankings.append((pair, score))
        
        # Сортируем по оценке (от самой высокой к самой низкой)
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings