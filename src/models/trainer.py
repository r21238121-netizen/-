"""
Model Training Module
Trains both traditional ML models (LightGBM) and neural networks (PyTorch)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import lightgbm as lgb
import optuna
import pandas as pd
import numpy as np
import joblib
import json
import os
import logging
from typing import Dict, List, Tuple, Optional, Union
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesDataset(Dataset):
    """Custom dataset for time series data"""
    def __init__(self, features: np.ndarray, targets: np.ndarray, sequence_length: int = 10):
        self.features = features
        self.targets = targets
        self.sequence_length = sequence_length
        
    def __len__(self):
        return len(self.features) - self.sequence_length + 1
    
    def __getitem__(self, idx):
        # For sequence models, return a sequence of features
        feature_seq = self.features[idx:idx + self.sequence_length]
        target = self.targets[idx + self.sequence_length - 1]  # Target for the last time step
        
        return torch.FloatTensor(feature_seq), torch.LongTensor([target]).squeeze()

class CNNLSTMModel(nn.Module):
    """CNN + LSTM model for time series prediction"""
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2, 
                 num_classes: int = 3, dropout: float = 0.2):
        super(CNNLSTMModel, self).__init__()
        
        # 1D CNN layers to extract local features
        self.cnn = nn.Sequential(
            nn.Conv1d(input_size, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(128),
        )
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=128,  # Output from CNN
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Fully connected layers
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, num_classes)
        )
        
    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)
        batch_size, seq_len, input_size = x.size()
        
        # Reshape for CNN: (batch_size, input_size, sequence_length)
        x = x.transpose(1, 2)
        
        # Apply CNN: (batch_size, cnn_output_channels, sequence_length)
        x = self.cnn(x)
        
        # Transpose back: (batch_size, sequence_length, cnn_output_channels)
        x = x.transpose(1, 2)
        
        # Apply LSTM
        lstm_out, (hidden, _) = self.lstm(x)
        
        # Use the last output
        output = self.classifier(lstm_out[:, -1, :])
        
        return output

class TransformerModel(nn.Module):
    """Transformer model for time series prediction"""
    def __init__(self, input_size: int, d_model: int = 64, nhead: int = 8, 
                 num_layers: int = 3, num_classes: int = 3, dropout: float = 0.1):
        super(TransformerModel, self).__init__()
        
        self.input_projection = nn.Linear(input_size, d_model)
        self.pos_encoder = nn.Embedding(1000, d_model)  # Positional encoding
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )
        
    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)
        batch_size, seq_len, input_size = x.size()
        
        # Project input to model dimension
        x = self.input_projection(x)  # (batch_size, seq_len, d_model)
        
        # Add positional encoding
        positions = torch.arange(0, seq_len, dtype=torch.long, device=x.device).unsqueeze(0)
        pos_encoding = self.pos_encoder(positions)  # (1, seq_len, d_model)
        x = x + pos_encoding
        
        # Apply transformer
        output = self.transformer_encoder(x)
        
        # Use the last output for classification
        output = self.classifier(output[:, -1, :])
        
        return output

class ModelTrainer:
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.config = {
            'model_type': 'lightgbm',  # 'lightgbm', 'cnn_lstm', 'transformer'
            'target_column': 'target_classification_5',
            'feature_columns': [],
            'sequence_length': 10,
            'batch_size': 64,
            'epochs': 100,
            'learning_rate': 0.001,
            'early_stopping_rounds': 10,
            'model_save_path': './models/',
            'scaler_save_path': './models/scaler.pkl',
            'model_config_path': './models/config.json'
        }
        
        # Load config if provided
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config.update(json.load(f))
        
        # Create model directory
        os.makedirs(self.config['model_save_path'], exist_ok=True)
        
        # Initialize model and scaler
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def prepare_data(self, df: pd.DataFrame, target_column: str = None) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and targets from DataFrame"""
        if target_column is None:
            target_column = self.config['target_column']
        
        # Identify feature columns (exclude timestamp, datetime, OHLCV, and target)
        exclude_cols = {'timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume', target_column}
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Store feature columns for later use
        self.feature_columns = feature_cols
        
        X = df[feature_cols].values
        y = df[target_column].values
        
        # Handle NaN values
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X = X[mask]
        y = y[mask]
        
        return X, y
    
    def train_lightgbm(self, X_train: np.ndarray, y_train: np.ndarray, 
                      X_val: np.ndarray, y_val: np.ndarray) -> lgb.Booster:
        """Train LightGBM model"""
        self.logger.info("Training LightGBM model...")
        
        # Convert to LightGBM dataset
        train_data = lgb.Dataset(X_train, label=y_train)
        val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
        
        # Default parameters
        params = {
            'objective': 'multiclass',
            'num_class': 3,  # LONG, SHORT, HOLD
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': 42
        }
        
        # Train the model
        model = lgb.train(
            params,
            train_data,
            valid_sets=[train_data, val_data],
            num_boost_round=1000,
            callbacks=[lgb.early_stopping(stopping_rounds=self.config['early_stopping_rounds'])],
            verbose_eval=False
        )
        
        # Evaluate on validation set
        y_pred = model.predict(X_val)
        y_pred_classes = np.argmax(y_pred, axis=1)
        
        accuracy = accuracy_score(y_val, y_pred_classes)
        precision = precision_score(y_val, y_pred_classes, average='weighted', zero_division=0)
        recall = recall_score(y_val, y_pred_classes, average='weighted', zero_division=0)
        f1 = f1_score(y_val, y_pred_classes, average='weighted', zero_division=0)
        
        self.logger.info(f"LightGBM Validation - Accuracy: {accuracy:.4f}, "
                        f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        
        return model
    
    def train_pytorch_model(self, model: nn.Module, train_loader: DataLoader, 
                           val_loader: DataLoader, device: torch.device) -> nn.Module:
        """Train PyTorch model"""
        self.logger.info("Training PyTorch model...")
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=self.config['learning_rate'])
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(self.config['epochs']):
            # Training phase
            model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for batch_features, batch_targets in train_loader:
                batch_features, batch_targets = batch_features.to(device), batch_targets.to(device)
                
                optimizer.zero_grad()
                outputs = model(batch_features)
                loss = criterion(outputs, batch_targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                _, predicted = outputs.max(1)
                train_total += batch_targets.size(0)
                train_correct += predicted.eq(batch_targets).sum().item()
            
            # Validation phase
            model.eval()
            val_loss = 0.0
            val_correct = 0
            val_total = 0
            
            with torch.no_grad():
                for batch_features, batch_targets in val_loader:
                    batch_features, batch_targets = batch_features.to(device), batch_targets.to(device)
                    
                    outputs = model(batch_features)
                    loss = criterion(outputs, batch_targets)
                    
                    val_loss += loss.item()
                    _, predicted = outputs.max(1)
                    val_total += batch_targets.size(0)
                    val_correct += predicted.eq(batch_targets).sum().item()
            
            train_loss /= len(train_loader)
            val_loss /= len(val_loader)
            train_acc = train_correct / train_total
            val_acc = val_correct / val_total
            
            self.logger.info(f"Epoch {epoch+1}/{self.config['epochs']} - "
                            f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
                            f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                torch.save(model.state_dict(), f"{self.config['model_save_path']}/best_model.pth")
            else:
                patience_counter += 1
                
            if patience_counter >= self.config['early_stopping_rounds']:
                self.logger.info(f"Early stopping at epoch {epoch+1}")
                break
                
            # Learning rate scheduling
            scheduler.step(val_loss)
        
        # Load best model
        model.load_state_dict(torch.load(f"{self.config['model_save_path']}/best_model.pth"))
        return model
    
    def train(self, df: pd.DataFrame = None, data_path: str = None):
        """Main training function"""
        if df is None and data_path is None:
            raise ValueError("Either df or data_path must be provided")
        
        if df is None:
            # Load data from path
            if data_path.endswith('.parquet'):
                df = pd.read_parquet(data_path)
            elif data_path.endswith('.csv'):
                df = pd.read_csv(data_path)
            else:
                raise ValueError("Data path must be .parquet or .csv file")
        
        self.logger.info(f"Starting model training with {len(df)} samples")
        
        # Prepare features and targets
        X, y = self.prepare_data(df)
        
        # Split data temporally
        n = len(X)
        train_end = int(n * 0.7)
        val_end = int(n * 0.85)
        
        X_train, X_val, X_test = X[:train_end], X[train_end:val_end], X[val_end:]
        y_train, y_val, y_test = y[:train_end], y[train_end:val_end], y[val_end:]
        
        self.logger.info(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Save scaler
        joblib.dump(self.scaler, self.config['scaler_save_path'])
        
        # Train model based on type
        if self.config['model_type'] == 'lightgbm':
            self.model = self.train_lightgbm(X_train_scaled, y_train, X_val_scaled, y_val)
            
            # Evaluate on test set
            y_pred = self.model.predict(X_test_scaled)
            y_pred_classes = np.argmax(y_pred, axis=1)
            
            accuracy = accuracy_score(y_test, y_pred_classes)
            precision = precision_score(y_test, y_pred_classes, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred_classes, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred_classes, average='weighted', zero_division=0)
            
            self.logger.info(f"Test Results - Accuracy: {accuracy:.4f}, "
                            f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
            
            # Save LightGBM model
            self.model.save_model(f"{self.config['model_save_path']}/lightgbm_model.txt")
            
        elif self.config['model_type'] in ['cnn_lstm', 'transformer']:
            # Use PyTorch model
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.logger.info(f"Using device: {device}")
            
            # Prepare sequence datasets
            train_dataset = TimeSeriesDataset(X_train_scaled, y_train, self.config['sequence_length'])
            val_dataset = TimeSeriesDataset(X_val_scaled, y_val, self.config['sequence_length'])
            test_dataset = TimeSeriesDataset(X_test_scaled, y_test, self.config['sequence_length'])
            
            train_loader = DataLoader(train_dataset, batch_size=self.config['batch_size'], shuffle=False)
            val_loader = DataLoader(val_dataset, batch_size=self.config['batch_size'], shuffle=False)
            test_loader = DataLoader(test_dataset, batch_size=self.config['batch_size'], shuffle=False)
            
            # Initialize model
            input_size = X_train_scaled.shape[1]
            if self.config['model_type'] == 'cnn_lstm':
                self.model = CNNLSTMModel(
                    input_size=input_size,
                    hidden_size=64,
                    num_layers=2,
                    num_classes=len(np.unique(y)),
                    dropout=0.2
                )
            else:  # transformer
                self.model = TransformerModel(
                    input_size=input_size,
                    d_model=64,
                    nhead=8,
                    num_layers=3,
                    num_classes=len(np.unique(y)),
                    dropout=0.1
                )
            
            self.model.to(device)
            
            # Train the model
            self.model = self.train_pytorch_model(self.model, train_loader, val_loader, device)
            
            # Evaluate on test set
            self.model.eval()
            test_correct = 0
            test_total = 0
            all_preds = []
            all_targets = []
            
            with torch.no_grad():
                for batch_features, batch_targets in test_loader:
                    batch_features, batch_targets = batch_features.to(device), batch_targets.to(device)
                    
                    outputs = self.model(batch_features)
                    _, predicted = outputs.max(1)
                    
                    test_total += batch_targets.size(0)
                    test_correct += predicted.eq(batch_targets).sum().item()
                    
                    all_preds.extend(predicted.cpu().numpy())
                    all_targets.extend(batch_targets.cpu().numpy())
            
            test_acc = test_correct / test_total
            test_precision = precision_score(all_targets, all_preds, average='weighted', zero_division=0)
            test_recall = recall_score(all_targets, all_preds, average='weighted', zero_division=0)
            test_f1 = f1_score(all_targets, all_preds, average='weighted', zero_division=0)
            
            self.logger.info(f"Test Results - Accuracy: {test_acc:.4f}, "
                            f"Precision: {test_precision:.4f}, Recall: {test_recall:.4f}, F1: {test_f1:.4f}")
            
            # Save PyTorch model
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'feature_columns': self.feature_columns,
                'model_type': self.config['model_type'],
                'sequence_length': self.config['sequence_length']
            }, f"{self.config['model_save_path']}/pytorch_model.pth")
        
        # Save model configuration
        config_to_save = self.config.copy()
        config_to_save['feature_columns'] = self.feature_columns
        with open(self.config['model_config_path'], 'w') as f:
            json.dump(config_to_save, f, indent=2)
        
        self.logger.info("Model training completed successfully")
        
        return self.model
    
    def hyperparameter_tuning(self, df: pd.DataFrame, n_trials: int = 50):
        """Perform hyperparameter tuning using Optuna"""
        def objective(trial):
            # Suggest hyperparameters based on model type
            if self.config['model_type'] == 'lightgbm':
                params = {
                    'objective': 'multiclass',
                    'num_class': 3,
                    'metric': 'multi_logloss',
                    'boosting_type': 'gbdt',
                    'num_leaves': trial.suggest_int('num_leaves', 20, 200),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                    'feature_fraction': trial.suggest_float('feature_fraction', 0.5, 1.0),
                    'bagging_fraction': trial.suggest_float('bagging_fraction', 0.5, 1.0),
                    'bagging_freq': trial.suggest_int('bagging_freq', 1, 10),
                    'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 1, 100),
                    'verbose': -1,
                    'random_state': 42
                }
                
                # Prepare data
                X, y = self.prepare_data(df)
                
                # Split data
                n = len(X)
                train_end = int(n * 0.7)
                val_end = int(n * 0.85)
                
                X_train, X_val = X[:train_end], X[train_end:val_end]
                y_train, y_val = y[:train_end], y[train_end:val_end]
                
                # Scale features
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_val_scaled = self.scaler.transform(X_val)
                
                # Convert to LightGBM datasets
                train_data = lgb.Dataset(X_train_scaled, label=y_train)
                val_data = lgb.Dataset(X_val_scaled, label=y_val, reference=train_data)
                
                # Train model
                model = lgb.train(
                    params,
                    train_data,
                    valid_sets=[val_data],
                    num_boost_round=100,
                    callbacks=[lgb.early_stopping(stopping_rounds=10)],
                    verbose_eval=False
                )
                
                # Evaluate
                y_pred = model.predict(X_val_scaled)
                y_pred_classes = np.argmax(y_pred, axis=1)
                accuracy = accuracy_score(y_val, y_pred_classes)
                
                return accuracy
            else:
                # For neural networks, we'll just return a dummy value for now
                # since neural network hyperparameter tuning is more complex
                return 0.5
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=n_trials)
        
        self.logger.info(f"Best parameters: {study.best_params}")
        self.logger.info(f"Best value: {study.best_value}")
        
        return study.best_params

# Example usage
if __name__ == "__main__":
    # Example of how to use the trainer
    # This would typically be called after data preprocessing
    trainer = ModelTrainer()
    
    # For demonstration, we'll create a mock dataset
    # In practice, you would load the preprocessed data
    print("Model trainer initialized. In practice, call trainer.train(df) with your preprocessed data.")