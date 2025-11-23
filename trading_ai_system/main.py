"""
Main Application File for AI Trading System
"""
import sys
import time
import threading
from datetime import datetime
import logging

from .api.binance_api import BinanceAPI
from .analysis.technical_analysis import TechnicalAnalyzer
from .trade_management.trade_manager import TradeManager
from .config import UPDATE_INTERVAL_SECONDS, LOG_LEVEL

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingAISystem:
    def __init__(self):
        self.api = BinanceAPI()
        self.analyzer = TechnicalAnalyzer()
        self.trade_manager = TradeManager(self.api)
        self.is_running = False
        self.monitoring_thread = None
        self.logger = logging.getLogger(__name__)
        
    def start_system(self):
        """Start the AI trading system"""
        self.logger.info("Starting AI Trading System...")
        self.is_running = True
        
        # Start market monitoring in a separate thread
        self.monitoring_thread = threading.Thread(target=self.monitor_markets, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("AI Trading System started successfully")
    
    def stop_system(self):
        """Stop the AI trading system"""
        self.logger.info("Stopping AI Trading System...")
        self.is_running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)  # Wait up to 2 seconds for thread to finish
        
        self.logger.info("AI Trading System stopped")
    
    def monitor_markets(self):
        """Main monitoring loop that runs in a separate thread"""
        while self.is_running:
            try:
                # Scan for trading opportunities
                opportunities = self.trade_manager.scan_markets()
                
                # Process high confidence opportunities
                for opportunity in opportunities[:3]:  # Process top 3 opportunities
                    if opportunity['confidence'] > 0.7:  # High confidence threshold
                        self.logger.info(f"High confidence signal found: {opportunity}")
                        
                        # In a real system, you might ask for confirmation before executing
                        # For demo purposes, we'll just log the opportunity
                        self.logger.info(f"Would execute trade: {opportunity['direction']} {opportunity['symbol']} with confidence {opportunity['confidence']:.2f}")
                
                # Wait before next scan
                time.sleep(UPDATE_INTERVAL_SECONDS)
                
            except Exception as e:
                self.logger.error(f"Error in market monitoring loop: {e}")
                time.sleep(UPDATE_INTERVAL_SECONDS)
    
    def get_system_status(self):
        """Get current system status"""
        return {
            'is_running': self.is_running,
            'available_capital': self.trade_manager.get_available_capital(),
            'current_mode': self.trade_manager.current_mode,
            'active_positions': 0,  # This would come from API in a real implementation
            'last_scan_time': datetime.now().isoformat()
        }
    
    def set_trading_mode(self, mode: str):
        """Set the trading mode"""
        self.trade_manager.set_trading_mode(mode)
    
    def manual_scan(self):
        """Perform a manual scan for trading opportunities"""
        self.logger.info("Manual market scan initiated")
        opportunities = self.trade_manager.scan_markets()
        return opportunities
    
    def get_top_assets(self, count: int = 5):
        """Get top assets for trading"""
        return self.trade_manager.get_top_assets(count)


def main():
    """Main function to run the trading system"""
    print("AI Trading System")
    print("="*50)
    print(f"Total Balance: $100")
    print(f"Available for Trading: ${100 * 0.29}")  # 29% of $100
    print("Available Trading Modes: Scalping, Spot, Long Term")
    print("\nStarting system...")
    
    # Create and start the trading system
    ai_system = TradingAISystem()
    
    try:
        ai_system.start_system()
        
        # Display system status
        status = ai_system.get_system_status()
        print(f"\nSystem Status: {status}")
        
        # Show top assets for trading
        print("\nTop assets for trading:")
        top_assets = ai_system.get_top_assets(5)
        for asset in top_assets:
            print(f"  {asset['symbol']}: Score = {asset['total_score']:.3f}")
        
        # Wait for user input
        print("\nSystem is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping system...")
        ai_system.stop_system()
        print("System stopped.")
    except Exception as e:
        print(f"Error running system: {e}")
        ai_system.stop_system()


if __name__ == "__main__":
    main()