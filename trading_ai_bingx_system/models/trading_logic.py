from api.bingx_api import BingXAPI
from analysis.technical_analysis import TechnicalAnalysis
from utils.risk_management import RiskManagement
from config.config import TRADE_MODES, TRADING_PAIRS, AUTO_EXECUTION
import time
import threading
from datetime import datetime
from typing import Dict, List

class TradingLogic:
    def __init__(self):
        self.api = BingXAPI()
        self.ta = TechnicalAnalysis()
        self.rm = RiskManagement()
        self.trade_modes = TRADE_MODES
        self.trading_pairs = TRADING_PAIRS
        self.auto_execution = AUTO_EXECUTION
        self.active_mode = "scalping"  # Режим по умолчанию
        self.running = False
        self.trade_thread = None
        
    def set_trade_mode(self, mode: str):
        """Установка режима торговли"""
        if mode in self.trade_modes:
            self.active_mode = mode
        else:
            raise ValueError(f"Неподдерживаемый режим торговли: {mode}")
    
    def get_market_data(self, pair: str, timeframe: str) -> List:
        """Получение рыночных данных для пары"""
        try:
            klines = self.api.get_kline_data(pair.replace('-', ''), timeframe)
            if 'data' in klines and klines['data']:
                return klines['data']
            else:
                print(f"Нет данных для {pair} на таймфрейме {timeframe}")
                return []
        except Exception as e:
            print(f"Ошибка получения данных для {pair}: {e}")
            return []
    
    def analyze_all_pairs(self) -> Dict:
        """Анализ всех торговых пар"""
        analysis_results = {}
        
        for pair in self.trading_pairs:
            # Получаем данные в зависимости от активного режима
            timeframe = self.trade_modes[self.active_mode]['timeframe']
            klines_data = self.get_market_data(pair, timeframe)
            
            if klines_data:
                pair_analysis = self.ta.analyze_pair(klines_data, pair)
                analysis_results[pair] = pair_analysis
        
        return analysis_results
    
    def find_trading_opportunities(self) -> List[Dict]:
        """Поиск торговых возможностей"""
        opportunities = []
        analysis_results = self.analyze_all_pairs()
        
        for pair, analysis in analysis_results.items():
            signal = analysis.get('signal', {})
            action = signal.get('action', 'HOLD')
            
            if action in ['BUY', 'SELL']:
                # Рассчитываем параметры позиции
                current_price = analysis.get('current_price', 0)
                
                if action == 'BUY':
                    stop_loss = self.rm.calculate_stop_loss(current_price, 'LONG')
                    take_profit = self.rm.calculate_take_profit(current_price, 'LONG')
                    position_info = self.rm.calculate_position_size(current_price, stop_loss)
                else:  # SELL
                    stop_loss = self.rm.calculate_stop_loss(current_price, 'SHORT')
                    take_profit = self.rm.calculate_take_profit(current_price, 'SHORT')
                    position_info = self.rm.calculate_position_size(current_price, stop_loss)
                
                opportunity = {
                    'pair': pair,
                    'action': action,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'position_size': position_info['position_size'],
                    'confidence': signal.get('confidence', 0),
                    'reasons': signal.get('reasons', []),
                    'indicators': analysis.get('indicators', {})
                }
                
                opportunities.append(opportunity)
        
        # Сортируем по уверенности
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        return opportunities
    
    def execute_trade(self, opportunity: Dict) -> Dict:
        """Выполнение сделки"""
        if not self.auto_execution:
            print(f"Рекомендация: {opportunity['action']} {opportunity['pair']} по цене {opportunity['entry_price']}")
            print(f"Размер позиции: {opportunity['position_size']}")
            print(f"Стоп-лосс: {opportunity['stop_loss']}")
            print(f"Тейк-профит: {opportunity['take_profit']}")
            print(f"Уверенность: {opportunity['confidence']}")
            return {"status": "recommendation_only", "opportunity": opportunity}
        
        try:
            # Определяем параметры ордера
            symbol = opportunity['pair'].replace('-', '')
            side = 'BUY' if opportunity['action'] == 'BUY' else 'SELL'
            position_side = 'LONG' if opportunity['action'] == 'BUY' else 'SHORT'
            
            # Получаем плечо для текущего режима
            leverage = self.trade_modes[self.active_mode]['leverage']
            
            # Выставляем ордер
            result = self.api.place_order(
                symbol=symbol,
                side=side,
                position_side=position_side,
                order_type='MARKET',
                quantity=opportunity['position_size'],
                stop_loss=opportunity['stop_loss'],
                take_profit=opportunity['take_profit']
            )
            
            return {
                "status": "executed",
                "result": result,
                "opportunity": opportunity
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "opportunity": opportunity
            }
    
    def rank_trading_pairs(self) -> List[tuple]:
        """Ранжирование торговых пар по потенциалу"""
        analysis_results = self.analyze_all_pairs()
        rankings = self.ta.rank_pairs(analysis_results)
        return rankings
    
    def start_trading(self):
        """Запуск автоматической торговли"""
        if self.running:
            print("Торговля уже запущена")
            return
        
        self.running = True
        self.trade_thread = threading.Thread(target=self._trading_loop)
        self.trade_thread.start()
        print(f"Автоматическая торговля запущена в режиме {self.active_mode}")
    
    def stop_trading(self):
        """Остановка автоматической торговли"""
        self.running = False
        if self.trade_thread:
            self.trade_thread.join()
        print("Торговля остановлена")
    
    def _trading_loop(self):
        """Основной цикл торговли"""
        interval = self.trade_modes[self.active_mode]['interval_seconds']
        
        while self.running:
            try:
                # Проверяем ограничения риска
                account_info = self.api.get_account_info()
                if 'data' in account_info and account_info['data']:
                    balance = float(account_info['data'][0].get('balance', 0))
                    pnl = float(account_info['data'][0].get('crossedUnPnl', 0))
                    
                    risk_check = self.rm.check_risk_limits(pnl, balance)
                    if not risk_check['can_trade']:
                        print(f"Торговля приостановлена: {risk_check['reason']}")
                        time.sleep(interval)
                        continue
                
                # Ищем торговые возможности
                opportunities = self.find_trading_opportunities()
                
                # Выполняем сделки с высокой уверенностью
                for opportunity in opportunities[:3]:  # Максимум 3 сделки за цикл
                    if opportunity['confidence'] > 0.5:  # Только высокая уверенность
                        result = self.execute_trade(opportunity)
                        if result['status'] == 'executed':
                            print(f"Сделка выполнена: {opportunity['action']} {opportunity['pair']}")
                        elif result['status'] == 'error':
                            print(f"Ошибка выполнения сделки: {result['error']}")
                
                # Ждем следующий интервал
                time.sleep(interval)
                
            except Exception as e:
                print(f"Ошибка в цикле торговли: {e}")
                time.sleep(interval)
    
    def get_account_status(self) -> Dict:
        """Получение статуса счета"""
        try:
            account_info = self.api.get_account_info()
            position_info = self.api.get_position_info()
            
            return {
                "account": account_info,
                "positions": position_info
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_current_recommendations(self) -> List[Dict]:
        """Получение текущих торговых рекомендаций"""
        opportunities = self.find_trading_opportunities()
        # Возвращаем только рекомендации с высокой уверенностью
        return [opp for opp in opportunities if opp['confidence'] > 0.4]