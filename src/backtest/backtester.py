"""
Backtesting Module
Realistic simulation of trading strategies with commission, slippage, and risk management
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional
import os
import json
from pathlib import Path

class Position:
    """Represents a trading position"""
    def __init__(self, entry_time, entry_price, size, side, stop_loss=None, take_profit=None):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.size = size  # Position size in contracts/tokens
        self.side = side  # 'LONG' or 'SHORT'
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.exit_time = None
        self.exit_price = None
        self.pnl = None
        
    def close(self, exit_time, exit_price):
        """Close the position and calculate PnL"""
        self.exit_time = exit_time
        self.exit_price = exit_price
        multiplier = 1 if self.side == 'LONG' else -1
        self.pnl = (exit_price - self.entry_price) * multiplier * self.size
        return self.pnl

class Backtester:
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.config = {
            'initial_capital': 10000,
            'commission_rate': 0.0005,  # 0.05% per trade
            'slippage_rate': 0.001,     # 0.1% slippage
            'risk_per_trade': 0.02,     # 2% risk per trade
            'max_drawdown': 0.10,       # 10% maximum drawdown
            'min_atr_threshold': 0.01,  # Minimum ATR for entry
            'leverage': 1,
            'results_path': './results/',
            'plots_path': './results/plots/'
        }
        
        # Load config if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config.update(json.load(f))
        
        # Create directories
        os.makedirs(self.config['results_path'], exist_ok=True)
        os.makedirs(self.config['plots_path'], exist_ok=True)
        
        # Initialize metrics
        self.metrics = {}
        self.trades = []
        self.equity_curve = []
        self.positions = []
        
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate necessary technical indicators for backtesting"""
        data = df.copy()
        
        # Calculate ATR for volatility filtering
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        data['atr_14'] = true_range.rolling(14).mean()
        
        # Calculate returns
        data['returns'] = data['close'].pct_change()
        
        # Calculate price volatility
        data['volatility_20'] = data['returns'].rolling(20).std()
        
        return data
    
    def run_backtest(self, df: pd.DataFrame, signals: pd.Series, 
                    model_name: str = "default") -> Dict:
        """
        Run backtest with given signals
        Signals should be -1 (SHORT), 0 (HOLD), 1 (LONG)
        """
        self.logger.info(f"Starting backtest with {len(df)} data points")
        
        # Calculate technical indicators
        data = self.calculate_technical_indicators(df)
        
        # Initialize backtest variables
        capital = self.config['initial_capital']
        equity = capital
        position = None
        trade_count = 0
        winning_trades = 0
        losing_trades = 0
        total_pnl = 0
        max_equity = capital
        max_drawdown = 0
        drawdown_start = None
        drawdown_end = None
        current_drawdown_start = None
        
        # Lists to store results
        self.equity_curve = [(data.index[0], equity)]
        self.trades = []
        
        # Process each time step
        for i in range(1, len(data)):
            current_bar = data.iloc[i]
            prev_bar = data.iloc[i-1]
            
            # Check if we have an open position
            if position is not None:
                # Check for exit conditions
                exit_triggered = False
                exit_price = None
                
                # Stop loss check
                if position.stop_loss:
                    if (position.side == 'LONG' and current_bar['low'] <= position.stop_loss) or \
                       (position.side == 'SHORT' and current_bar['high'] >= position.stop_loss):
                        exit_price = position.stop_loss
                        exit_triggered = True
                
                # Take profit check
                if not exit_triggered and position.take_profit:
                    if (position.side == 'LONG' and current_bar['high'] >= position.take_profit) or \
                       (position.side == 'SHORT' and current_bar['low'] <= position.take_profit):
                        exit_price = position.take_profit
                        exit_triggered = True
                
                # Close position if exit condition met
                if exit_triggered:
                    # Use actual exit price based on stop/take profit
                    pnl = position.close(current_bar.name, exit_price)
                    
                    # Calculate net PnL after commission
                    entry_commission = position.entry_price * position.size * self.config['commission_rate']
                    exit_commission = exit_price * position.size * self.config['commission_rate']
                    net_pnl = pnl - entry_commission - exit_commission
                    
                    # Update capital
                    capital += net_pnl
                    total_pnl += net_pnl
                    
                    # Update trade statistics
                    if net_pnl > 0:
                        winning_trades += 1
                    else:
                        losing_trades += 1
                    
                    self.trades.append({
                        'entry_time': position.entry_time,
                        'exit_time': position.exit_time,
                        'entry_price': position.entry_price,
                        'exit_price': position.exit_price,
                        'side': position.side,
                        'size': position.size,
                        'gross_pnl': pnl,
                        'commissions': entry_commission + exit_commission,
                        'net_pnl': net_pnl,
                        'pnl_percent': net_pnl / position.entry_price / position.size
                    })
                    
                    position = None
                    trade_count += 1
                    self.logger.debug(f"Closed position at {exit_price}, net PnL: {net_pnl:.2f}")
            
            # Check for entry conditions if no position is open
            if position is None and i < len(signals) and pd.notna(signals.iloc[i]):
                signal = int(signals.iloc[i])
                
                # Only enter if signal is LONG (1) or SHORT (-1)
                if signal != 0:
                    # Check ATR threshold
                    if current_bar['atr_14'] < self.config['min_atr_threshold']:
                        continue  # Skip entry if volatility is too low
                    
                    # Calculate position size based on risk management
                    risk_amount = capital * self.config['risk_per_trade']
                    entry_price = current_bar['close']
                    
                    # Simple stop loss based on ATR
                    atr_multiple = 2
                    if signal == 1:  # LONG
                        stop_loss = entry_price - (current_bar['atr_14'] * atr_multiple)
                        side = 'LONG'
                    else:  # SHORT
                        stop_loss = entry_price + (current_bar['atr_14'] * atr_multiple)
                        side = 'SHORT'
                    
                    # Calculate position size
                    risk_per_unit = abs(entry_price - stop_loss)
                    position_size = risk_amount / risk_per_unit
                    
                    # Apply leverage
                    position_size *= self.config['leverage']
                    
                    # Create position
                    position = Position(
                        entry_time=current_bar.name,
                        entry_price=entry_price,
                        size=position_size,
                        side=side,
                        stop_loss=stop_loss
                    )
                    
                    self.logger.debug(f"Opened {side} position at {entry_price}, size: {position_size:.4f}")
            
            # Update equity curve
            if position is not None:
                # Calculate unrealized PnL
                current_price = current_bar['close']
                multiplier = 1 if position.side == 'LONG' else -1
                unrealized_pnl = (current_price - position.entry_price) * multiplier * position.size
                
                # Calculate net equity (capital + unrealized PnL - commissions paid so far)
                entry_commission = position.entry_price * position.size * self.config['commission_rate']
                current_equity = capital + unrealized_pnl - entry_commission
            else:
                current_equity = capital
            
            self.equity_curve.append((current_bar.name, current_equity))
            
            # Track drawdown
            if current_equity > max_equity:
                max_equity = current_equity
                current_drawdown_start = None
            else:
                drawdown = (max_equity - current_equity) / max_equity
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    drawdown_end = current_bar.name
                    if current_drawdown_start:
                        drawdown_start = current_drawdown_start
                
                if drawdown > 0 and current_drawdown_start is None:
                    current_drawdown_start = current_bar.name
            
            # Check maximum drawdown stop out
            if max_drawdown > self.config['max_drawdown']:
                self.logger.warning(f"Maximum drawdown threshold reached: {max_drawdown:.2%}")
                break
        
        # Calculate final metrics
        total_return = (current_equity - self.config['initial_capital']) / self.config['initial_capital']
        total_trades = len(self.trades)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate Sharpe ratio (assuming 252 trading days)
        if len(self.equity_curve) > 1:
            equity_returns = np.diff([x[1] for x in self.equity_curve]) / [x[1] for x in self.equity_curve][:-1]
            if len(equity_returns) > 0 and np.std(equity_returns) != 0:
                sharpe_ratio = np.mean(equity_returns) / np.std(equity_returns) * np.sqrt(252)
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # Calculate profit factor
        total_profit = sum(trade['net_pnl'] for trade in self.trades if trade['net_pnl'] > 0)
        total_loss = abs(sum(trade['net_pnl'] for trade in self.trades if trade['net_pnl'] < 0))
        profit_factor = total_profit / total_loss if total_loss != 0 else float('inf')
        
        # Calculate maximum runup (similar to max drawdown but for gains)
        max_runup = 0
        min_equity = self.config['initial_capital']
        for _, equity in self.equity_curve:
            if equity < min_equity:
                min_equity = equity
            else:
                runup = (equity - min_equity) / min_equity
                max_runup = max(max_runup, runup)
        
        # Store metrics
        self.metrics = {
            'total_return': total_return,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'drawdown_start': drawdown_start,
            'drawdown_end': drawdown_end,
            'sharpe_ratio': sharpe_ratio,
            'profit_factor': profit_factor,
            'max_runup': max_runup,
            'final_equity': current_equity,
            'initial_capital': self.config['initial_capital'],
            'model_name': model_name
        }
        
        self.logger.info(f"Backtest completed - Total Return: {total_return:.2%}, "
                        f"Win Rate: {win_rate:.2%}, Max Drawdown: {max_drawdown:.2%}")
        
        return self.metrics
    
    def plot_results(self, save_path: Optional[str] = None):
        """Plot backtest results"""
        if not self.equity_curve:
            self.logger.warning("No equity curve data to plot")
            return
        
        if save_path is None:
            save_path = f"{self.config['plots_path']}/backtest_results.png"
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Backtest Results', fontsize=16)
        
        # Equity curve
        times = [x[0] for x in self.equity_curve]
        values = [x[1] for x in self.equity_curve]
        
        axes[0, 0].plot(times, values, label='Equity', color='blue')
        axes[0, 0].axhline(y=self.config['initial_capital'], color='red', linestyle='--', label='Initial Capital')
        axes[0, 0].set_title('Equity Curve')
        axes[0, 0].set_ylabel('Equity ($)')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Drawdown
        initial_cap = self.config['initial_capital']
        running_max = np.maximum.accumulate(values)
        drawdown = (running_max - values) / running_max
        axes[0, 1].fill_between(times, 0, drawdown, color='red', alpha=0.3, label='Drawdown')
        axes[0, 1].set_title('Drawdown')
        axes[0, 1].set_ylabel('Drawdown (%)')
        axes[0, 1].grid(True)
        
        # Trade PnL distribution
        if self.trades:
            pnl_values = [trade['net_pnl'] for trade in self.trades]
            axes[1, 0].hist(pnl_values, bins=30, color='skyblue', edgecolor='black')
            axes[1, 0].set_title('Distribution of Trade PnL')
            axes[1, 0].set_xlabel('PnL ($)')
            axes[1, 0].set_ylabel('Frequency')
            axes[1, 0].grid(True)
        
        # Monthly returns (if we have enough data)
        if len(self.equity_curve) > 30:  # At least 30 data points
            df_equity = pd.DataFrame(self.equity_curve, columns=['time', 'equity'])
            df_equity.set_index('time', inplace=True)
            
            # Resample to monthly if we have daily data
            try:
                monthly_returns = df_equity['equity'].resample('M').last().pct_change()
                monthly_returns = monthly_returns.dropna()
                
                axes[1, 1].bar(range(len(monthly_returns)), monthly_returns.values, 
                              color=['green' if x >= 0 else 'red' for x in monthly_returns.values])
                axes[1, 1].set_title('Monthly Returns')
                axes[1, 1].set_ylabel('Return (%)')
                axes[1, 1].grid(True)
            except:
                axes[1, 1].text(0.5, 0.5, 'Not enough data\nfor monthly returns', 
                               horizontalalignment='center', verticalalignment='center',
                               transform=axes[1, 1].transAxes)
        else:
            axes[1, 1].text(0.5, 0.5, 'Insufficient data\nfor monthly returns', 
                           horizontalalignment='center', verticalalignment='center',
                           transform=axes[1, 1].transAxes)
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        self.logger.info(f"Results plotted and saved to {save_path}")
    
    def save_results(self, results_path: Optional[str] = None):
        """Save backtest results to file"""
        if results_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_path = f"{self.config['results_path']}/backtest_results_{timestamp}.json"
        
        results = {
            'metrics': self.metrics,
            'trades': self.trades,
            'equity_curve': self.equity_curve,
            'config': self.config
        }
        
        with open(results_path, 'w') as f:
            json.dump(results, f, default=str, indent=2)
        
        self.logger.info(f"Results saved to {results_path}")
    
    def run(self, data_path: str, signals_path: str = None, signals: pd.Series = None, 
            model_path: str = None, model_name: str = "default"):
        """Main backtest runner"""
        # Load data
        if data_path.endswith('.parquet'):
            df = pd.read_parquet(data_path)
        elif data_path.endswith('.csv'):
            df = pd.read_csv(data_path, index_col=0, parse_dates=True)
        else:
            raise ValueError("Data path must be .parquet or .csv file")
        
        # Load or use provided signals
        if signals is None:
            if signals_path:
                if signals_path.endswith('.parquet'):
                    signals_df = pd.read_parquet(signals_path)
                elif signals_path.endswith('.csv'):
                    signals_df = pd.read_csv(signals_path, index_col=0, parse_dates=True)
                else:
                    raise ValueError("Signals path must be .parquet or .csv file")
                
                # Assume the signal column is named 'signal' or 'predictions'
                if 'signal' in signals_df.columns:
                    signals = signals_df['signal']
                elif 'predictions' in signals_df.columns:
                    signals = signals_df['predictions']
                elif len(signals_df.columns) == 1:
                    signals = signals_df.iloc[:, 0]
                else:
                    raise ValueError("Could not identify signal column in signals data")
            else:
                # If no signals provided, we'll need to load a model and generate predictions
                if model_path is None:
                    raise ValueError("Either signals or model_path must be provided")
                
                # Load model and generate predictions (simplified - in practice would be more complex)
                self.logger.warning("Model loading for prediction not implemented in this version. "
                                   "Please provide pre-generated signals.")
                return None
        
        # Run backtest
        metrics = self.run_backtest(df, signals, model_name)
        
        # Generate plots
        self.plot_results()
        
        # Save results
        self.save_results()
        
        return metrics

# Example usage
if __name__ == "__main__":
    # Example of how to use the backtester
    # This would typically be called after model prediction
    backtester = Backtester()
    
    # For demonstration, we'll create a mock dataset and signals
    print("Backtester initialized. In practice, call backtester.run() with your data and signals.")