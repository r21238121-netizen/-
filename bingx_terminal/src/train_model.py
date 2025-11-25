"""
AI Model Training Script for BingX Terminal
This script handles the training of the trading prediction model
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def calculate_technical_indicators(df):
    """
    Calculate technical indicators for the dataset
    """
    # Price-based indicators
    df['price_change'] = df['close'].pct_change()
    df['high_low_pct'] = (df['high'] - df['low']) / df['open']
    df['price_change_vol'] = df['price_change'].rolling(window=10).std()
    
    # Moving averages
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_ratio'] = df['sma_10'] / df['sma_20']
    
    # RSI (Relative Strength Index)
    def calculate_rsi(prices, window=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    df['rsi'] = calculate_rsi(df['close'])
    
    # MACD (Moving Average Convergence Divergence)
    exp1 = df['close'].ewm(span=12).mean()
    exp2 = df['close'].ewm(span=26).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
    df['bb_width'] = df['bb_upper'] - df['bb_lower']
    df['bb_position'] = (df['close'] - df['bb_lower']) / df['bb_width']
    
    # Volume indicators
    df['volume_sma'] = df['volume'].rolling(window=10).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma']
    
    return df

def prepare_training_data(kline_data):
    """
    Prepare training data from kline data
    """
    # Convert kline data to DataFrame
    df = pd.DataFrame(kline_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'quote_asset_volume', 'number_of_trades', 
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    # Convert to numeric
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col])
    
    # Calculate technical indicators
    df = calculate_technical_indicators(df)
    
    # Create target variable (next period's price movement)
    df['future_close'] = df['close'].shift(-1)  # Next period's close
    df['future_return'] = ((df['future_close'] - df['close']) / df['close']) * 100
    
    # Create target classes: 0 = SELL/Down, 1 = HOLD/Same, 2 = BUY/Up
    df['target'] = 1  # Default to HOLD
    df.loc[df['future_return'] > 0.2, 'target'] = 2  # BUY if return > 0.2%
    df.loc[df['future_return'] < -0.2, 'target'] = 0  # SELL if return < -0.2%
    
    # Select features for training
    feature_columns = [
        'open', 'high', 'low', 'close', 'volume',
        'price_change', 'high_low_pct', 'price_change_vol',
        'sma_ratio', 'rsi', 'macd', 'macd_histogram',
        'bb_position', 'volume_ratio'
    ]
    
    # Remove rows with NaN values
    df = df.dropna()
    
    # Prepare features (X) and target (y)
    X = df[feature_columns].values
    y = df['target'].values
    
    return X, y, df[feature_columns]

def generate_mock_data(symbol="BTC-USDT", days=30, interval="1h"):
    """
    Generate mock kline data for testing purposes
    In a real scenario, this would fetch data from BingX API
    """
    print(f"Generating mock data for {symbol} over {days} days...")
    
    data = []
    base_price = 40000  # Starting price
    current_time = datetime.now() - timedelta(days=days)
    
    for i in range(days * 24):  # Hours in the specified days
        timestamp = int(current_time.timestamp() * 1000)  # Convert to milliseconds
        
        # Generate price with some random walk
        change_percent = (np.random.random() - 0.5) * 0.02  # -1% to +1% change
        open_price = base_price
        high_price = base_price * (1 + abs(np.random.random() * 0.01))
        low_price = base_price * (1 - abs(np.random.random() * 0.01))
        close_price = open_price * (1 + change_percent)
        
        # Ensure high >= close >= low
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        volume = np.random.random() * 1000  # Random volume
        
        data.append([
            timestamp,
            str(open_price),
            str(high_price),
            str(low_price),
            str(close_price),
            str(volume),
            timestamp + 3600000,  # close_time (1 hour later)
            str(volume * close_price),  # quote_asset_volume
            str(np.random.randint(100, 1000)),  # number_of_trades
            str(volume * 0.4),  # taker_buy_base_asset_volume
            str(volume * close_price * 0.4),  # taker_buy_quote_asset_volume
            "0"
        ])
        
        base_price = close_price
        current_time += timedelta(hours=1)
    
    return data

def train_model(symbol="BTC-USDT", save_path="models/trading_model.pkl", scaler_path="models/scaler.pkl"):
    """
    Train the AI model with historical data
    """
    print(f"Starting training for {symbol}...")
    
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Generate or load training data
    # In a real implementation, you would fetch this from the BingX API
    kline_data = generate_mock_data(symbol, days=60)  # 60 days of 1h data
    
    # Prepare features and target
    X, y, feature_df = prepare_training_data(kline_data)
    
    if len(X) == 0:
        print("No valid data for training")
        return None, None
    
    print(f"Training data shape: {X.shape}")
    print(f"Target distribution: {np.bincount(y)}")
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Normalize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train the model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    print("Training the model...")
    model.fit(X_train_scaled, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['SELL', 'HOLD', 'BUY']))
    
    # Save the model and scaler
    with open(save_path, 'wb') as f:
        pickle.dump(model, f)
    
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    print(f"\nModel saved to {save_path}")
    print(f"Scaler saved to {scaler_path}")
    
    return model, scaler

def load_model(model_path="models/trading_model.pkl", scaler_path="models/scaler.pkl"):
    """
    Load the trained model and scaler
    """
    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        print("Model files not found. Please train the model first.")
        return None, None
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    print(f"Model loaded from {model_path}")
    print(f"Scaler loaded from {scaler_path}")
    
    return model, scaler

def predict_with_model(model, scaler, features):
    """
    Make a prediction using the trained model
    """
    if model is None or scaler is None:
        print("Model or scaler is not loaded")
        return None
    
    # Ensure features is 2D array
    if len(features.shape) == 1:
        features = features.reshape(1, -1)
    
    # Scale the features
    features_scaled = scaler.transform(features)
    
    # Make prediction
    prediction = model.predict(features_scaled)[0]
    probabilities = model.predict_proba(features_scaled)[0]
    
    # Map prediction to signal
    signal_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
    signal = signal_map.get(prediction, 'HOLD')
    
    # Get confidence (probability of predicted class)
    confidence = max(probabilities) * 100
    
    return {
        'signal': signal,
        'confidence': confidence,
        'prediction': prediction,
        'probabilities': {
            'SELL': probabilities[0] * 100 if len(probabilities) > 0 else 0,
            'HOLD': probabilities[1] * 100 if len(probabilities) > 1 else 0,
            'BUY': probabilities[2] * 100 if len(probabilities) > 2 else 0
        }
    }

if __name__ == "__main__":
    # Train the model
    print("Starting AI model training for BingX Terminal...")
    
    # Train model for BTC-USDT
    model, scaler = train_model("BTC-USDT")
    
    if model and scaler:
        print("\nTraining completed successfully!")
        
        # Example prediction with mock features (these would come from real market data)
        # Using the same features as defined in prepare_training_data
        mock_features = np.array([
            40000.0,   # open
            40100.0,   # high
            39900.0,   # low
            40050.0,   # close
            1000.0,    # volume
            0.00125,   # price_change
            0.005,     # high_low_pct
            0.0008,    # price_change_vol
            1.001,     # sma_ratio
            55.0,      # rsi
            5.2,       # macd
            0.8,       # macd_histogram
            0.65,      # bb_position
            1.2        # volume_ratio
        ]).reshape(1, -1)
        
        result = predict_with_model(model, scaler, mock_features)
        if result:
            print(f"\nExample prediction: {result['signal']} with {result['confidence']:.2f}% confidence")
            print(f"Probabilities - SELL: {result['probabilities']['SELL']:.2f}%, "
                  f"HOLD: {result['probabilities']['HOLD']:.2f}%, "
                  f"BUY: {result['probabilities']['BUY']:.2f}%")
    else:
        print("Training failed!")