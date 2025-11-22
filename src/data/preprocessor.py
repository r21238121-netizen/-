"""
Data Preprocessing Module
Generates technical features and target variables for model training
"""

import pandas as pd
import numpy as np
import ta
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
import logging
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators and features
        """
        # Make a copy to avoid modifying original data
        data = df.copy()
        
        # Basic price features
        data['returns'] = data['close'].pct_change()
        data['log_returns'] = np.log(data['close'] / data['close'].shift(1))
        
        # Normalized candles
        data['norm_open'] = (data['open'] - data['close'].shift(1)) / data['close'].shift(1)
        data['norm_high'] = (data['high'] - data['close'].shift(1)) / data['close'].shift(1)
        data['norm_low'] = (data['low'] - data['close'].shift(1)) / data['close'].shift(1)
        data['norm_close'] = (data['close'] - data['close'].shift(1)) / data['close'].shift(1)
        
        # EMA indicators
        data['ema_9'] = EMAIndicator(close=data['close'], window=9).ema_indicator()
        data['ema_21'] = EMAIndicator(close=data['close'], window=21).ema_indicator()
        data['ema_50'] = EMAIndicator(close=data['close'], window=50).ema_indicator()
        
        # EMA ratios and spreads
        data['ema_9_21_ratio'] = data['ema_9'] / data['ema_21']
        data['ema_9_50_ratio'] = data['ema_9'] / data['ema_50']
        data['ema_21_50_ratio'] = data['ema_21'] / data['ema_50']
        
        data['ema_9_21_spread'] = data['ema_9'] - data['ema_21']
        data['ema_9_50_spread'] = data['ema_9'] - data['ema_50']
        data['ema_21_50_spread'] = data['ema_21'] - data['ema_50']
        
        # RSI (14)
        data['rsi_14'] = RSIIndicator(close=data['close'], window=14).rsi()
        
        # MACD
        macd_indicator = MACD(close=data['close'])
        data['macd'] = macd_indicator.macd()
        data['macd_signal'] = macd_indicator.macd_signal()
        data['macd_histogram'] = macd_indicator.macd_diff()
        
        # ATR (14) and volatility
        atr_indicator = AverageTrueRange(high=data['high'], low=data['low'], close=data['close'], window=14)
        data['atr_14'] = atr_indicator.average_true_range()
        data['atr_percent'] = data['atr_14'] / data['close']
        
        # Volatility measures
        data['volatility_14'] = data['returns'].rolling(window=14).std() * np.sqrt(252)
        data['volatility_7'] = data['returns'].rolling(window=7).std() * np.sqrt(252)
        
        # Volume features
        data['volume_sma_10'] = data['volume'].rolling(window=10).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma_10']
        data['volume_change'] = data['volume'].pct_change()
        
        # Price position relative to recent highs/lows
        data['high_5d'] = data['high'].rolling(window=5).max()
        data['low_5d'] = data['low'].rolling(window=5).min()
        data['price_position_5d'] = (data['close'] - data['low_5d']) / (data['high_5d'] - data['low_5d'])
        
        data['high_20d'] = data['high'].rolling(window=20).max()
        data['low_20d'] = data['low'].rolling(window=20).min()
        data['price_position_20d'] = (data['close'] - data['low_20d']) / (data['high_20d'] - data['low_20d'])
        
        # Bollinger Bands
        data['bb_middle'] = data['close'].rolling(window=20).mean()
        bb_std = data['close'].rolling(window=20).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
        data['bb_width'] = data['bb_upper'] - data['bb_lower']
        data['bb_position'] = (data['close'] - data['bb_lower']) / data['bb_width']
        
        # Lag features
        for lag in [1, 2, 3, 5, 10]:
            data[f'returns_lag_{lag}'] = data['returns'].shift(lag)
            data[f'volume_lag_{lag}'] = data['volume'].shift(lag)
            data[f'high_lag_{lag}'] = data['high'].shift(lag)
            data[f'low_lag_{lag}'] = data['low'].shift(lag)
        
        # Rolling statistics
        for window in [5, 10, 20]:
            data[f'returns_mean_{window}'] = data['returns'].rolling(window=window).mean()
            data[f'returns_std_{window}'] = data['returns'].rolling(window=window).std()
            data[f'volume_mean_{window}'] = data['volume'].rolling(window=window).mean()
            data[f'close_mean_{window}'] = data['close'].rolling(window=window).mean()
        
        # Price change features
        data['high_low_pct'] = (data['high'] - data['low']) / data['close']
        data['open_close_pct'] = (data['close'] - data['open']) / data['open']
        
        # Trend features
        data['trend_ema'] = np.where(data['ema_9'] > data['ema_21'], 1, 0)
        data['trend_rsi'] = np.where(data['rsi_14'] > 50, 1, 0)
        
        # Normalize features where appropriate
        feature_cols = [col for col in data.columns if col not in ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']]
        
        for col in feature_cols:
            if data[col].dtype in ['float64', 'int64']:
                # Avoid division by zero
                std_val = data[col].std()
                if std_val != 0 and not pd.isna(std_val):
                    data[f'{col}_norm'] = (data[col] - data[col].mean()) / std_val
        
        return data
    
    def create_targets(self, df: pd.DataFrame, prediction_horizon: int = 5, 
                      commission_rate: float = 0.0005) -> pd.DataFrame:
        """
        Create target variables for classification and regression
        """
        data = df.copy()
        
        # Future returns for regression targets
        data['future_return_1'] = data['close'].shift(-1) / data['close'] - 1
        data['future_return_5'] = data['close'].shift(-prediction_horizon) / data['close'] - 1
        data['future_return_10'] = data['close'].shift(-10) / data['close'] - 1
        
        # Classification targets based on future returns with commission adjustment
        # LONG: future return > commission threshold
        # SHORT: future return < -commission threshold  
        # HOLD: otherwise
        
        # For 5-period horizon
        threshold = commission_rate * prediction_horizon  # Adjust for holding period
        data['target_classification_5'] = 0  # Default to HOLD
        data['target_classification_5'] = np.where(
            data['future_return_5'] > threshold, 1,  # LONG
            np.where(data['future_return_5'] < -threshold, -1, 0)  # SHORT or HOLD
        )
        
        # For 1-period horizon
        data['target_classification_1'] = 0  # Default to HOLD
        data['target_classification_1'] = np.where(
            data['future_return_1'] > commission_rate, 1,  # LONG
            np.where(data['future_return_1'] < -commission_rate, -1, 0)  # SHORT or HOLD
        )
        
        # Binary classification (long/short only)
        data['target_binary_5'] = np.where(data['future_return_5'] > 0, 1, 0)
        data['target_binary_1'] = np.where(data['future_return_1'] > 0, 1, 0)
        
        # Multi-class target with more granular categories
        data['target_multiclass_5'] = 0
        data['target_multiclass_5'] = np.where(
            data['future_return_5'] > threshold * 2, 2,  # Strong LONG
            np.where(
                data['future_return_5'] > threshold, 1,  # Weak LONG
                np.where(
                    data['future_return_5'] < -threshold * 2, -2,  # Strong SHORT
                    np.where(data['future_return_5'] < -threshold, -1, 0)  # Weak SHORT or HOLD
                )
            )
        )
        
        return data
    
    def prepare_dataset(self, df: pd.DataFrame, prediction_horizon: int = 5, 
                       commission_rate: float = 0.0005, 
                       feature_windows: List[int] = [10, 20, 50]) -> pd.DataFrame:
        """
        Complete preprocessing pipeline: calculate features and targets
        """
        self.logger.info("Starting feature calculation...")
        df_with_features = self.calculate_features(df)
        
        self.logger.info("Creating target variables...")
        df_with_targets = self.create_targets(df_with_features, prediction_horizon, commission_rate)
        
        # Add sequence windows for time series models
        for window in feature_windows:
            self.logger.info(f"Adding sequence features for window {window}...")
            # For time series models, we might want to create rolling window features
            for col in ['close', 'volume', 'returns']:
                if col in df_with_targets.columns:
                    # Create rolling statistics for the window
                    df_with_targets[f'{col}_rolling_mean_{window}'] = df_with_targets[col].rolling(window=window).mean()
                    df_with_targets[f'{col}_rolling_std_{window}'] = df_with_targets[col].rolling(window=window).std()
                    df_with_targets[f'{col}_rolling_min_{window}'] = df_with_targets[col].rolling(window=window).min()
                    df_with_targets[f'{col}_rolling_max_{window}'] = df_with_targets[col].rolling(window=window).max()
        
        # Remove rows with NaN values (due to rolling calculations)
        initial_len = len(df_with_targets)
        df_cleaned = df_with_targets.dropna()
        final_len = len(df_cleaned)
        
        self.logger.info(f"Removed {initial_len - final_len} rows with NaN values. "
                        f"Dataset size: {final_len} -> {initial_len}")
        
        return df_cleaned
    
    def split_data(self, df: pd.DataFrame, train_ratio: float = 0.7, 
                   val_ratio: float = 0.15, test_ratio: float = 0.15) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Temporal split of data (no random shuffling to prevent data leakage)
        """
        n = len(df)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))
        
        train_df = df.iloc[:train_end]
        val_df = df.iloc[train_end:val_end]
        test_df = df.iloc[val_end:]
        
        self.logger.info(f"Data split - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        
        return train_df, val_df, test_df

# Example usage
if __name__ == "__main__":
    # Example of how to use the preprocessor
    # This would typically be called after data collection
    preprocessor = DataPreprocessor()
    
    # Example: create a mock DataFrame with OHLCV data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='1D')
    n = len(dates)
    
    mock_data = pd.DataFrame({
        'timestamp': range(len(dates)),
        'datetime': dates,
        'open': np.random.uniform(30000, 70000, n),
        'high': np.random.uniform(30000, 70000, n),
        'low': np.random.uniform(30000, 70000, n),
        'close': np.random.uniform(30000, 70000, n),
        'volume': np.random.uniform(1000, 10000, n)
    })
    
    # Ensure OHLC order is correct
    for i in range(1, n):
        mock_data.loc[i, 'open'] = mock_data.loc[i-1, 'close']
        mock_data.loc[i, 'high'] = max(mock_data.loc[i, 'open'], 
                                      mock_data.loc[i, 'close'] + np.random.uniform(0, 1000))
        mock_data.loc[i, 'low'] = min(mock_data.loc[i, 'open'], 
                                     mock_data.loc[i, 'close'] - np.random.uniform(0, 1000))
    
    processed_data = preprocessor.prepare_dataset(mock_data)
    print(f"Processed dataset shape: {processed_data.shape}")
    print(f"Feature columns: {len([col for col in processed_data.columns if 'feature' in col or 'indicator' in col or 'norm' in col or 'lag' in col or 'rolling' in col or 'atr' in col or 'volatility' in col or 'rsi' in col or 'macd' in col or 'ema' in col or 'bb' in col or 'trend' in col or 'position' in col or 'ratio' in col or 'spread' in col or 'width' in col])} features created")