import math
from config.config import RISK_CAPITAL, MAX_POSITION_SIZE_PERCENT, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT

class RiskManagement:
    def __init__(self):
        self.risk_capital = RISK_CAPITAL  # Капитал, доступный для риска (например, 29 из 100$)
        
    def calculate_position_size(self, entry_price: float, stop_loss_price: float, balance_portion: float = 1.0) -> dict:
        """
        Рассчитывает размер позиции на основе риска
        :param entry_price: Цена входа
        :param stop_loss_price: Цена стоп-лосса
        :param balance_portion: Доля доступного капитала для использования (0.0 - 1.0)
        :return: Словарь с информацией о позиции
        """
        max_risk_per_trade = self.risk_capital * balance_portion * (STOP_LOSS_PERCENT / 100)
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit == 0:
            return {
                "position_size": 0,
                "risk_amount": 0,
                "leverage": 0
            }
        
        position_size = max_risk_per_trade / risk_per_unit
        
        # Ограничиваем размер позиции
        max_position_size = self.risk_capital * (MAX_POSITION_SIZE_PERCENT / 100) / entry_price
        position_size = min(position_size, max_position_size)
        
        return {
            "position_size": round(position_size, 6),
            "risk_amount": round(max_risk_per_trade, 2),
            "leverage": round((position_size * entry_price) / (self.risk_capital * balance_portion), 2)
        }
    
    def calculate_stop_loss(self, entry_price: float, direction: str, risk_percent: float = None) -> float:
        """
        Рассчитывает цену стоп-лосса
        :param entry_price: Цена входа
        :param direction: 'LONG' или 'SHORT'
        :param risk_percent: Процент риска (если None, использует значение из конфига)
        :return: Цена стоп-лосса
        """
        if risk_percent is None:
            risk_percent = STOP_LOSS_PERCENT
            
        if direction.upper() == 'LONG':
            stop_loss = entry_price * (1 - risk_percent / 100)
        elif direction.upper() == 'SHORT':
            stop_loss = entry_price * (1 + risk_percent / 100)
        else:
            raise ValueError("Direction must be 'LONG' or 'SHORT'")
            
        return round(stop_loss, 6)
    
    def calculate_take_profit(self, entry_price: float, direction: str, reward_ratio: float = 2.0) -> float:
        """
        Рассчитывает цену тейк-профита на основе отношения риск/прибыль
        :param entry_price: Цена входа
        :param direction: 'LONG' или 'SHORT'
        :param reward_ratio: Отношение прибыли к риску (например, 2.0 означает 2:1)
        :return: Цена тейк-профита
        """
        stop_loss_distance = abs(entry_price - self.calculate_stop_loss(entry_price, direction))
        profit_distance = stop_loss_distance * reward_ratio
        
        if direction.upper() == 'LONG':
            take_profit = entry_price + profit_distance
        elif direction.upper() == 'SHORT':
            take_profit = entry_price - profit_distance
        else:
            raise ValueError("Direction must be 'LONG' or 'SHORT'")
            
        return round(take_profit, 6)
    
    def check_risk_limits(self, current_pnl: float, total_balance: float) -> dict:
        """
        Проверяет, не превышены ли лимиты риска
        :param current_pnl: Текущая прибыль/убыток
        :param total_balance: Общий баланс
        :return: Словарь с информацией о риске
        """
        max_drawdown = self.risk_capital * (STOP_LOSS_PERCENT / 100)  # Максимальная просадка на одну сделку
        
        risk_status = {
            "can_trade": True,
            "reason": "",
            "max_loss_reached": False,
            "max_balance_risk_reached": False
        }
        
        # Проверяем, не превышена ли максимальная просадка
        if current_pnl <= -max_drawdown:
            risk_status["can_trade"] = False
            risk_status["reason"] = "Превышена максимальная просадка на одну сделку"
            risk_status["max_loss_reached"] = True
        
        # Проверяем, не превышено ли максимальное использование баланса
        if total_balance < (self.risk_capital * 0.1):  # Если осталось меньше 10% рискового капитала
            risk_status["can_trade"] = False
            risk_status["reason"] = "Слишком маленький баланс для торговли"
            risk_status["max_balance_risk_reached"] = True
            
        return risk_status
    
    def adjust_position_for_balance(self, position_size: float, entry_price: float, available_balance: float, leverage: float = 1) -> float:
        """
        Корректирует размер позиции в соответствии с доступным балансом
        :param position_size: Предлагаемый размер позиции
        :param entry_price: Цена входа
        :param available_balance: Доступный баланс
        :param leverage: Используемое плечо
        :return: Скорректированный размер позиции
        """
        max_position_by_balance = (available_balance * leverage) / entry_price
        adjusted_position = min(position_size, max_position_by_balance)
        
        return round(adjusted_position, 6)
    
    def calculate_margin_requirement(self, position_size: float, entry_price: float, leverage: float) -> float:
        """
        Рассчитывает требуемую маржу для позиции
        :param position_size: Размер позиции
        :param entry_price: Цена входа
        :param leverage: Плечо
        :return: Требуемая маржа
        """
        position_value = position_size * entry_price
        margin_required = position_value / leverage
        
        return round(margin_required, 6)

    def get_trading_recommendation(self, signal_confidence: float, risk_to_reward: float, volatility: float) -> str:
        """
        Возвращает рекомендацию по торговле на основе различных факторов
        :param signal_confidence: Уверенность сигнала (0-1)
        :param risk_to_reward: Отношение риск/прибыль
        :param volatility: Волатильность актива
        :return: Рекомендация ('STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL')
        """
        score = 0
        
        # Оценка уверенности сигнала (вес 40%)
        score += signal_confidence * 40
        
        # Оценка отношения риск/прибыль (вес 30%)
        if risk_to_reward >= 2.0:
            score += 30
        elif risk_to_reward >= 1.5:
            score += 20
        elif risk_to_reward >= 1.0:
            score += 10
            
        # Оценка волатильности (вес 30%)
        # Высокая волатильность может быть как хорошей, так и плохой
        if 0.8 <= volatility <= 1.2:  # Средняя волатильность
            score += 30
        elif 0.5 <= volatility <= 0.8 or 1.2 < volatility <= 2.0:  # Умеренная волатильность
            score += 20
        else:  # Слишком высокая или низкая волатильность
            score += 10
            
        if score >= 80:
            return "STRONG_BUY"
        elif score >= 60:
            return "BUY"
        elif score >= 40:
            return "HOLD"
        elif score >= 20:
            return "SELL"
        else:
            return "STRONG_SELL"