"""
GUI Module for Trading Agent
Main window with tabs for data, training, backtesting, and trading
"""

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
                              QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit,
                              QGroupBox, QFormLayout, QProgressBar, QFileDialog,
                              QMessageBox, QSplitter)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon
import json
import os
import logging
from pathlib import Path

class DataTab(QWidget):
    """Data collection tab"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Configuration group
        config_group = QGroupBox("Data Collection Configuration")
        config_layout = QFormLayout()
        
        self.pair_input = QLineEdit("BTC-USDT")
        config_layout.addRow("Trading Pair:", self.pair_input)
        
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["1m", "5m", "15m", "1h", "4h", "1d"])
        config_layout.addRow("Timeframe:", self.timeframe_combo)
        
        self.days_input = QLineEdit("30")
        config_layout.addRow("Days Back:", self.days_input)
        
        config_group.setLayout(config_layout)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        self.collect_btn = QPushButton("Collect Data")
        self.load_btn = QPushButton("Load Data")
        
        btn_layout.addWidget(self.collect_btn)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addStretch()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels(["Datetime", "Open", "High", "Low", "Close", "Volume"])
        
        # Add all to main layout
        layout.addWidget(config_group)
        layout.addLayout(btn_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.data_table)
        
        self.setLayout(layout)

class TrainingTab(QWidget):
    """Model training tab"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Configuration group
        config_group = QGroupBox("Training Configuration")
        config_layout = QFormLayout()
        
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["LightGBM", "CNN-LSTM", "Transformer"])
        config_layout.addRow("Model Type:", self.model_type_combo)
        
        self.target_combo = QComboBox()
        self.target_combo.addItems(["target_classification_5", "target_classification_1", "target_binary_5"])
        config_layout.addRow("Target Column:", self.target_combo)
        
        self.epochs_input = QLineEdit("100")
        config_layout.addRow("Epochs:", self.epochs_input)
        
        self.batch_size_input = QLineEdit("64")
        config_layout.addRow("Batch Size:", self.batch_size_input)
        
        self.learning_rate_input = QLineEdit("0.001")
        config_layout.addRow("Learning Rate:", self.learning_rate_input)
        
        config_group.setLayout(config_layout)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        self.train_btn = QPushButton("Start Training")
        self.load_data_btn = QPushButton("Load Training Data")
        self.hyperopt_btn = QPushButton("Hyperparameter Tuning")
        
        btn_layout.addWidget(self.load_data_btn)
        btn_layout.addWidget(self.train_btn)
        btn_layout.addWidget(self.hyperopt_btn)
        btn_layout.addStretch()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        
        # Metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        
        # Add all to main layout
        layout.addWidget(config_group)
        layout.addLayout(btn_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Training Results:"))
        layout.addWidget(self.results_text)
        layout.addWidget(QLabel("Metrics:"))
        layout.addWidget(self.metrics_table)
        
        self.setLayout(layout)

class BacktestTab(QWidget):
    """Backtesting tab"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Configuration group
        config_group = QGroupBox("Backtest Configuration")
        config_layout = QFormLayout()
        
        self.model_path_input = QLineEdit("./models/best_model.pth")
        self.model_path_btn = QPushButton("Browse...")
        
        model_path_layout = QHBoxLayout()
        model_path_layout.addWidget(self.model_path_input)
        model_path_layout.addWidget(self.model_path_btn)
        
        config_layout.addRow("Model Path:", model_path_layout)
        
        self.initial_capital_input = QLineEdit("10000")
        config_layout.addRow("Initial Capital:", self.initial_capital_input)
        
        self.commission_input = QLineEdit("0.0005")
        config_layout.addRow("Commission Rate:", self.commission_input)
        
        self.risk_per_trade_input = QLineEdit("0.02")
        config_layout.addRow("Risk per Trade:", self.risk_per_trade_input)
        
        config_group.setLayout(config_layout)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        self.run_backtest_btn = QPushButton("Run Backtest")
        self.load_data_btn = QPushButton("Load Data")
        self.load_signals_btn = QPushButton("Load Signals")
        
        btn_layout.addWidget(self.load_data_btn)
        btn_layout.addWidget(self.load_signals_btn)
        btn_layout.addWidget(self.run_backtest_btn)
        btn_layout.addStretch()
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        
        # Performance metrics table
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        
        # Equity curve placeholder
        self.equity_plot_label = QLabel("Equity curve will appear here after backtest")
        self.equity_plot_label.setAlignment(Qt.AlignCenter)
        self.equity_plot_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
        self.equity_plot_label.setMinimumHeight(200)
        
        # Add all to main layout
        layout.addWidget(config_group)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Backtest Results:"))
        layout.addWidget(self.results_text)
        layout.addWidget(QLabel("Performance Metrics:"))
        layout.addWidget(self.metrics_table)
        layout.addWidget(QLabel("Equity Curve:"))
        layout.addWidget(self.equity_plot_label)
        
        self.setLayout(layout)

class TradingTab(QWidget):
    """Live trading tab"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Configuration group
        config_group = QGroupBox("Trading Configuration")
        config_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        config_layout.addRow("API Key:", self.api_key_input)
        
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setEchoMode(QLineEdit.Password)
        config_layout.addRow("Secret Key:", self.secret_key_input)
        
        self.selected_model_input = QLineEdit("./models/best_model.pth")
        self.model_browse_btn = QPushButton("Browse...")
        
        model_layout = QHBoxLayout()
        model_layout.addWidget(self.selected_model_input)
        model_layout.addWidget(self.model_browse_btn)
        
        config_layout.addRow("Selected Model:", model_layout)
        
        self.pair_combo = QComboBox()
        self.pair_combo.addItems(["BTC-USDT", "ETH-USDT", "BNB-USDT", "SOL-USDT"])
        config_layout.addRow("Trading Pair:", self.pair_combo)
        
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["1m", "5m", "15m", "1h"])
        config_layout.addRow("Timeframe:", self.timeframe_combo)
        
        config_group.setLayout(config_layout)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Trading")
        self.stop_btn = QPushButton("Stop Trading")
        self.pause_btn = QPushButton("Pause")
        
        self.start_btn.setStyleSheet("background-color: lightgreen;")
        self.stop_btn.setStyleSheet("background-color: lightcoral;")
        self.pause_btn.setStyleSheet("background-color: lightyellow;")
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        
        # Trading status
        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("font-weight: bold; color: blue;")
        
        # Positions table
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(5)
        self.positions_table.setHorizontalHeaderLabels(["Pair", "Side", "Size", "Entry Price", "PnL"])
        
        # Trades table
        self.trades_table = QTableWidget()
        self.trades_table.setColumnCount(6)
        self.trades_table.setHorizontalHeaderLabels(["Time", "Pair", "Side", "Price", "Size", "PnL"])
        
        # Add all to main layout
        layout.addWidget(config_group)
        layout.addLayout(btn_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(QLabel("Current Positions:"))
        layout.addWidget(self.positions_table)
        layout.addWidget(QLabel("Recent Trades:"))
        layout.addWidget(self.trades_table)
        
        self.setLayout(layout)

class LogTab(QWidget):
    """Log display tab"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("Clear Log")
        self.save_log_btn = QPushButton("Save Log")
        
        btn_layout.addWidget(self.clear_log_btn)
        btn_layout.addStretch()
        
        # Add to layout
        layout.addLayout(btn_layout)
        layout.addWidget(self.log_display)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BingX AI Trading Agent")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.data_tab = DataTab()
        self.training_tab = TrainingTab()
        self.backtest_tab = BacktestTab()
        self.trading_tab = TradingTab()
        self.log_tab = LogTab()
        
        # Add tabs to widget
        self.tab_widget.addTab(self.data_tab, "Data")
        self.tab_widget.addTab(self.training_tab, "Training")
        self.tab_widget.addTab(self.backtest_tab, "Backtest")
        self.tab_widget.addTab(self.trading_tab, "Trading")
        self.tab_widget.addTab(self.log_tab, "Log")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Set up logging
        self.setup_logging()
        
        # Connect signals
        self.connect_signals()
    
    def setup_logging(self):
        """Set up logging to display in the log tab"""
        # Create a custom handler that emits to the log tab
        class QtHandler(logging.Handler):
            def __init__(self, log_tab):
                super().__init__()
                self.log_tab = log_tab
            
            def emit(self, record):
                msg = self.format(record)
                # Use Qt's thread-safe mechanism to update UI
                self.log_tab.log_display.append(msg)
        
        # Create and configure the handler
        handler = QtHandler(self.log_tab)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add handler to root logger
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
        
        # Add initial log message
        logging.info("BingX AI Trading Agent GUI initialized")
    
    def connect_signals(self):
        """Connect button signals to their respective functions"""
        # Data tab
        self.data_tab.collect_btn.clicked.connect(self.collect_data)
        self.data_tab.load_btn.clicked.connect(self.load_data)
        
        # Training tab
        self.training_tab.train_btn.clicked.connect(self.start_training)
        self.training_tab.load_data_btn.clicked.connect(self.load_training_data)
        self.training_tab.hyperopt_btn.clicked.connect(self.run_hyperopt)
        
        # Backtest tab
        self.backtest_tab.run_backtest_btn.clicked.connect(self.run_backtest)
        self.backtest_tab.load_data_btn.clicked.connect(self.load_backtest_data)
        self.backtest_tab.load_signals_btn.clicked.connect(self.load_signals)
        self.backtest_tab.model_path_btn.clicked.connect(self.browse_model)
        
        # Trading tab
        self.trading_tab.start_btn.clicked.connect(self.start_trading)
        self.trading_tab.stop_btn.clicked.connect(self.stop_trading)
        self.trading_tab.pause_btn.clicked.connect(self.pause_trading)
        self.trading_tab.model_browse_btn.clicked.connect(self.browse_trading_model)
        
        # Log tab
        self.log_tab.clear_log_btn.clicked.connect(self.clear_log)
        self.log_tab.save_log_btn.clicked.connect(self.save_log)
    
    # Placeholder methods for button functionality
    def collect_data(self):
        logging.info("Starting data collection...")
        pair = self.data_tab.pair_input.text()
        timeframe = self.data_tab.timeframe_combo.currentText()
        days = self.data_tab.days_input.text()
        logging.info(f"Collecting {days} days of {timeframe} data for {pair}")
        # In a real implementation, this would call the data collection module
        
    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Data", "", "Parquet Files (*.parquet);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            logging.info(f"Loading data from {file_path}")
            # In a real implementation, this would load the data and display it in the table
    
    def start_training(self):
        logging.info("Starting model training...")
        model_type = self.training_tab.model_type_combo.currentText()
        target = self.training_tab.target_combo.currentText()
        logging.info(f"Training {model_type} model with target {target}")
        # In a real implementation, this would call the training module
    
    def load_training_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Training Data", "", "Parquet Files (*.parquet);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            logging.info(f"Loading training data from {file_path}")
    
    def run_hyperopt(self):
        logging.info("Starting hyperparameter optimization...")
        # In a real implementation, this would call the hyperparameter tuning module
    
    def run_backtest(self):
        logging.info("Running backtest...")
        model_path = self.backtest_tab.model_path_input.text()
        initial_capital = float(self.backtest_tab.initial_capital_input.text())
        logging.info(f"Running backtest with model {model_path} and capital {initial_capital}")
        # In a real implementation, this would call the backtest module
    
    def load_backtest_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Backtest Data", "", "Parquet Files (*.parquet);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            logging.info(f"Loading backtest data from {file_path}")
    
    def load_signals(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Signals", "", "Parquet Files (*.parquet);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            logging.info(f"Loading signals from {file_path}")
    
    def browse_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Model", "", "Model Files (*.pth *.txt);;All Files (*)"
        )
        if file_path:
            self.backtest_tab.model_path_input.setText(file_path)
    
    def start_trading(self):
        logging.info("Starting live trading...")
        api_key = self.trading_tab.api_key_input.text()
        secret_key = self.trading_tab.secret_key_input.text()
        model_path = self.trading_tab.selected_model_input.text()
        
        if not api_key or not secret_key:
            QMessageBox.warning(self, "Warning", "Please enter API keys")
            return
        
        logging.info("Live trading started")
        self.trading_tab.status_label.setText("Status: Trading")
        self.trading_tab.status_label.setStyleSheet("font-weight: bold; color: green;")
    
    def stop_trading(self):
        logging.info("Stopping live trading...")
        logging.info("Trading stopped")
        self.trading_tab.status_label.setText("Status: Stopped")
        self.trading_tab.status_label.setStyleSheet("font-weight: bold; color: red;")
    
    def pause_trading(self):
        logging.info("Pausing trading...")
        self.trading_tab.status_label.setText("Status: Paused")
        self.trading_tab.status_label.setStyleSheet("font-weight: bold; color: orange;")
    
    def browse_trading_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Trading Model", "", "Model Files (*.pth *.txt);;All Files (*)"
        )
        if file_path:
            self.trading_tab.selected_model_input.setText(file_path)
    
    def clear_log(self):
        self.log_tab.log_display.clear()
        logging.info("Log cleared")
    
    def save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Log", "trading_log.txt", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.log_tab.log_display.toPlainText())
            logging.info(f"Log saved to {file_path}")

def run_gui():
    """Run the GUI application"""
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Arial", 9)
    app.setFont(font)
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Run the application
    sys.exit(app.exec())

# Example usage
if __name__ == "__main__":
    run_gui()