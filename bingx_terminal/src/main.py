"""
BingX Local AI Trading Terminal
Main Application File
"""
import os
import sys
import json
import time
import threading
import requests
import websocket
import pandas as pd
import numpy as np
from datetime import datetime
import webview
from cryptography.fernet import Fernet
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle

class BingXTerminal:
    def __init__(self):
        self.api_key = ""
        self.secret_key = ""
        self.base_url = "https://open-api.bingx.com"
        self.demo_mode = False
        self.listen_key = None
        self.ws_public = None
        self.ws_private = None
        self.encrypted_keys_file = "encrypted_keys.dat"
        self.model_file = "models/trading_model.pkl"
        self.scaler_file = "models/scaler.pkl"
        
        # Initialize AI model
        self.model = None
        self.scaler = None
        self.load_or_create_model()
        
        # Trading data storage
        self.market_data = {}
        self.positions = {}
        self.orders = {}
        
    def load_or_create_model(self):
        """Load existing model or create a new one"""
        try:
            if os.path.exists(self.model_file):
                with open(self.model_file, 'rb') as f:
                    self.model = pickle.load(f)
            else:
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        except:
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            
        try:
            if os.path.exists(self.scaler_file):
                with open(self.scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)
            else:
                self.scaler = StandardScaler()
        except:
            self.scaler = StandardScaler()
    
    def save_model(self):
        """Save the trained model"""
        os.makedirs("models", exist_ok=True)
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.scaler_file, 'wb') as f:
            pickle.dump(self.scaler, f)
    
    def encrypt_keys(self, api_key, secret_key):
        """Encrypt API keys using Fernet encryption"""
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        encrypted_data = {
            'api_key': cipher.encrypt(api_key.encode()).decode(),
            'secret_key': cipher.encrypt(secret_key.encode()).decode()
        }
        
        with open(self.encrypted_keys_file, 'wb') as f:
            f.write(key + b'\n' + json.dumps(encrypted_data).encode())
    
    def decrypt_keys(self):
        """Decrypt API keys"""
        if not os.path.exists(self.encrypted_keys_file):
            return None, None
            
        with open(self.encrypted_keys_file, 'rb') as f:
            content = f.read()
            key_end = content.find(b'\n')
            key = content[:key_end]
            encrypted_data = json.loads(content[key_end+1:].decode())
            
        cipher = Fernet(key)
        api_key = cipher.decrypt(encrypted_data['api_key'].encode()).decode()
        secret_key = cipher.decrypt(encrypted_data['secret_key'].encode()).decode()
        
        return api_key, secret_key
    
    def set_api_credentials(self, api_key, secret_key, demo=False):
        """Set API credentials and mode"""
        self.api_key = api_key
        self.secret_key = secret_key
        self.demo_mode = demo
        self.encrypt_keys(api_key, secret_key)
    
    def get_signature(self, timestamp, recvWindow=5000):
        """Generate signature for API requests"""
        import hmac
        import hashlib
        
        if self.demo_mode:
            # Demo mode might have different requirements
            pass
            
        # Create signature string
        signature_string = f"{self.api_key}{timestamp}{recvWindow}"
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def make_request(self, method, endpoint, params=None, signed=False):
        """Make API request to BingX"""
        import hmac
        import hashlib
        from urllib.parse import urlencode
        
        headers = {
            'X-BX-APIKEY': self.api_key
        }
        
        if signed:
            timestamp = str(int(time.time() * 1000))
            recvWindow = 5000
            
            # Create signature
            if params is None:
                params = {}
            params['timestamp'] = timestamp
            params['recvWindow'] = recvWindow
            
            query_string = urlencode(sorted(params.items()))
            signature_string = query_string
            signature = hmac.new(
                self.secret_key.encode('utf-8'),
                signature_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            params['signature'] = signature
        
        url = self.base_url + endpoint
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, params=params)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, params=params)
        
        return response.json()

    # Account and Balance Methods
    def get_balance(self):
        """Get account balance"""
        return self.make_request('GET', '/openApi/swap/v3/user/balance', signed=True)
    
    def get_positions(self):
        """Get current positions"""
        return self.make_request('GET', '/openApi/swap/v2/user/positions', signed=True)
    
    def get_income_history(self):
        """Get income history"""
        return self.make_request('GET', '/openApi/swap/v2/user/income', signed=True)
    
    # Trading Methods
    def place_order(self, symbol, side, positionSide, type, quantity, price=None, timeInForce="GTC"):
        """Place a new order"""
        params = {
            'symbol': symbol,
            'side': side,  # BUY or SELL
            'positionSide': positionSide,  # LONG or SHORT
            'type': type,  # LIMIT, MARKET, etc.
            'quantity': quantity
        }
        
        if price:
            params['price'] = price
        if timeInForce:
            params['timeInForce'] = timeInForce
            
        return self.make_request('POST', '/openApi/swap/v2/trade/order', params=params, signed=True)
    
    def cancel_order(self, symbol, orderId):
        """Cancel an order"""
        params = {
            'symbol': symbol,
            'orderId': orderId
        }
        return self.make_request('DELETE', '/openApi/swap/v2/trade/order', params=params, signed=True)
    
    def close_position(self, symbol, positionSide):
        """Close a position"""
        params = {
            'symbol': symbol,
            'positionSide': positionSide
        }
        return self.make_request('POST', '/openApi/swap/v1/trade/closePosition', params=params, signed=True)
    
    def get_open_orders(self, symbol=None):
        """Get open orders"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self.make_request('GET', '/openApi/swap/v2/trade/openOrders', params=params, signed=True)
    
    # Market Data Methods
    def get_klines(self, symbol, interval="1m", limit=500):
        """Get kline/candlestick data"""
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        return self.make_request('GET', '/openApi/swap/v2/quote/klines', params=params)
    
    def get_depth(self, symbol, limit=100):
        """Get order book depth"""
        params = {
            'symbol': symbol,
            'limit': limit
        }
        return self.make_request('GET', '/openApi/swap/v2/quote/depth', params=params)
    
    def get_ticker(self, symbol=None):
        """Get ticker information"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self.make_request('GET', '/openApi/swap/v2/quote/ticker', params=params)
    
    def get_24hr_ticker(self, symbol=None):
        """Get 24hr ticker information"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self.make_request('GET', '/openApi/swap/v2/quote/ticker/24hr', params=params)
    
    # AI Model Methods
    def prepare_features(self, kline_data, depth_data):
        """Prepare features for the AI model"""
        df = pd.DataFrame(kline_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'close_time', 'quote_asset_volume', 'number_of_trades', 
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # Convert to numeric
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        # Calculate technical indicators
        df['price_change'] = df['close'].pct_change()
        df['volatility'] = df['close'].rolling(window=10).std()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['rsi'] = self.calculate_rsi(df['close'])
        df['macd'] = self.calculate_macd(df['close'])
        
        # Prepare features from depth data
        bids = depth_data.get('bids', [])[:10]  # Top 10 bids
        asks = depth_data.get('asks', [])[:10]  # Top 10 asks
        
        bid_volumes = [float(bid[1]) for bid in bids]
        ask_volumes = [float(ask[1]) for ask in asks]
        
        total_bid_volume = sum(bid_volumes)
        total_ask_volume = sum(ask_volumes)
        
        # Combine all features
        features = {
            'current_price': float(df['close'].iloc[-1]),
            'price_change': df['price_change'].iloc[-1] if not pd.isna(df['price_change'].iloc[-1]) else 0,
            'volatility': df['volatility'].iloc[-1] if not pd.isna(df['volatility'].iloc[-1]) else 0,
            'sma_10_ratio': df['close'].iloc[-1] / df['sma_10'].iloc[-1] if not pd.isna(df['sma_10'].iloc[-1]) else 1,
            'sma_20_ratio': df['close'].iloc[-1] / df['sma_20'].iloc[-1] if not pd.isna(df['sma_20'].iloc[-1]) else 1,
            'rsi': df['rsi'].iloc[-1] if not pd.isna(df['rsi'].iloc[-1]) else 50,
            'macd': df['macd'].iloc[-1] if not pd.isna(df['macd'].iloc[-1]) else 0,
            'bid_ask_ratio': total_bid_volume / (total_ask_volume + 1e-8),  # Avoid division by zero
            'total_bid_volume': total_bid_volume,
            'total_ask_volume': total_ask_volume
        }
        
        return list(features.values())
    
    def calculate_rsi(self, prices, window=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()
        return macd - signal_line
    
    def predict_signal(self, symbol):
        """Generate AI trading signal for a symbol"""
        try:
            # Get market data
            klines = self.get_klines(symbol, interval="1m", limit=100)
            depth = self.get_depth(symbol, limit=20)
            
            if 'data' in klines and klines['data']:
                features = self.prepare_features(klines['data'], depth)
                
                # Reshape for prediction if needed
                features_array = np.array(features).reshape(1, -1)
                
                # Scale features
                if self.scaler:
                    features_scaled = self.scaler.transform(features_array)
                else:
                    features_scaled = features_array
                
                # Make prediction
                prediction = self.model.predict(features_scaled)[0]
                probability = self.model.predict_proba(features_scaled)[0]
                
                # Determine signal
                if prediction == 0:
                    signal = "SELL"
                    confidence = max(probability[0], 0) * 100
                elif prediction == 1:
                    signal = "BUY"
                    confidence = max(probability[1], 0) * 100
                else:
                    signal = "HOLD"
                    confidence = max(probability[2], 0) * 100 if len(probability) > 2 else 0
                
                return {
                    'symbol': symbol,
                    'signal': signal,
                    'confidence': round(confidence, 2),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error generating prediction: {e}")
            return {
                'symbol': symbol,
                'signal': "HOLD",
                'confidence': 0,
                'error': str(e)
            }
    
    def train_model(self, historical_data):
        """Train the AI model with historical data"""
        try:
            X = []
            y = []
            
            for data_point in historical_data:
                if 'features' in data_point and 'target' in data_point:
                    X.append(data_point['features'])
                    y.append(data_point['target'])
            
            if X and y:
                X = np.array(X)
                y = np.array(y)
                
                # Scale features
                X_scaled = self.scaler.fit_transform(X)
                
                # Train model
                self.model.fit(X_scaled, y)
                
                # Save the trained model
                self.save_model()
                
                return True
        except Exception as e:
            print(f"Error training model: {e}")
            return False

def main():
    # Create the application instance
    terminal = BingXTerminal()
    
    # Create the webview window with the HTML interface
    webview.create_window(
        'BingX Local AI Trading Terminal', 
        url='assets/index.html',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False
    )
    
    # Start the webview application
    webview.start(debug=True)

if __name__ == "__main__":
    main()