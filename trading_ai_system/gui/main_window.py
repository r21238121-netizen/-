"""
GUI Module for AI Trading System
Creates a Windows executable interface for the trading system
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
import logging

from ..main import TradingAISystem


class TradingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Trading System")
        self.root.geometry("800x600")
        
        # Initialize the trading system
        self.trading_system = TradingAISystem()
        
        # Setup logging to display in GUI
        self.setup_logging()
        
        # Create the interface
        self.create_widgets()
        
        # Start system status update
        self.update_status()
    
    def setup_logging(self):
        """Setup logging to display in the GUI"""
        class GuiHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.insert(tk.END, msg + '\n')
                self.text_widget.see(tk.END)
        
        # Add handler to root logger
        gui_handler = GuiHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)
        logging.getLogger().setLevel(logging.INFO)
    
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Create main frames
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        status_frame = ttk.LabelFrame(self.root, text="System Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        
        log_frame = ttk.LabelFrame(self.root, text="System Log", padding="10")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        
        analysis_frame = ttk.LabelFrame(self.root, text="Market Analysis", padding="10")
        analysis_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)
        
        # Control frame widgets
        ttk.Label(control_frame, text="Trading Mode:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.mode_var = tk.StringVar(value="scalping")
        mode_combo = ttk.Combobox(control_frame, textvariable=self.mode_var, 
                                 values=["scalping", "spot", "long_term"], state="readonly")
        mode_combo.grid(row=0, column=1, padx=(0, 10))
        mode_combo.bind('<<ComboboxSelected>>', self.change_trading_mode)
        
        self.start_stop_btn = ttk.Button(control_frame, text="Start System", command=self.toggle_system)
        self.start_stop_btn.grid(row=0, column=2, padx=(0, 5))
        
        ttk.Button(control_frame, text="Manual Scan", command=self.manual_scan).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(control_frame, text="Refresh Assets", command=self.refresh_assets).grid(row=0, column=4)
        
        # Status frame widgets
        self.status_labels = {}
        ttk.Label(status_frame, text="System Running:").grid(row=0, column=0, sticky=tk.W)
        self.status_labels['running'] = ttk.Label(status_frame, text="No")
        self.status_labels['running'].grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        ttk.Label(status_frame, text="Available Capital:").grid(row=0, column=2, sticky=tk.W)
        self.status_labels['capital'] = ttk.Label(status_frame, text="$0.00")
        self.status_labels['capital'].grid(row=0, column=3, sticky=tk.W, padx=(10, 20))
        
        ttk.Label(status_frame, text="Current Mode:").grid(row=1, column=0, sticky=tk.W)
        self.status_labels['mode'] = ttk.Label(status_frame, text="scalping")
        self.status_labels['mode'].grid(row=1, column=1, sticky=tk.W, padx=(10, 20))
        
        ttk.Label(status_frame, text="Active Positions:").grid(row=1, column=2, sticky=tk.W)
        self.status_labels['positions'] = ttk.Label(status_frame, text="0")
        self.status_labels['positions'].grid(row=1, column=3, sticky=tk.W, padx=(10, 20))
        
        # Log frame widgets
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Analysis frame widgets
        ttk.Label(analysis_frame, text="Top Assets for Trading:").grid(row=0, column=0, sticky=tk.W)
        
        self.assets_text = scrolledtext.ScrolledText(analysis_frame, height=6)
        self.assets_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        
        ttk.Button(analysis_frame, text="View Opportunities", command=self.show_opportunities).grid(row=2, column=0, pady=(5, 0))
        ttk.Button(analysis_frame, text="Execute Selected", command=self.execute_selected).grid(row=2, column=1, pady=(5, 0), padx=(5, 0))
        
        # Configure weights for resizing
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(1, weight=1)
    
    def change_trading_mode(self, event=None):
        """Change the trading mode"""
        new_mode = self.mode_var.get()
        self.trading_system.set_trading_mode(new_mode)
        logging.info(f"Trading mode changed to: {new_mode}")
    
    def toggle_system(self):
        """Start or stop the trading system"""
        if not self.trading_system.is_running:
            # Start the system
            self.trading_system.start_system()
            self.start_stop_btn.config(text="Stop System")
            logging.info("Trading system started")
        else:
            # Stop the system
            self.trading_system.stop_system()
            self.start_stop_btn.config(text="Start System")
            logging.info("Trading system stopped")
    
    def manual_scan(self):
        """Perform a manual market scan"""
        logging.info("Manual scan initiated")
        
        # Run scan in a separate thread to avoid GUI freezing
        scan_thread = threading.Thread(target=self._perform_manual_scan, daemon=True)
        scan_thread.start()
    
    def _perform_manual_scan(self):
        """Perform the actual scan (run in separate thread)"""
        try:
            opportunities = self.trading_system.manual_scan()
            logging.info(f"Found {len(opportunities)} trading opportunities")
            
            if opportunities:
                for opp in opportunities[:5]:  # Show top 5
                    direction = opp['direction'].upper()
                    conf = opp['confidence']
                    logging.info(f"Opportunity: {direction} {opp['symbol']} (Confidence: {conf:.2f})")
        except Exception as e:
            logging.error(f"Error during manual scan: {e}")
    
    def refresh_assets(self):
        """Refresh the top assets display"""
        logging.info("Refreshing top assets")
        
        # Run in separate thread to avoid GUI freezing
        asset_thread = threading.Thread(target=self._refresh_assets, daemon=True)
        asset_thread.start()
    
    def _refresh_assets(self):
        """Refresh assets in a separate thread"""
        try:
            top_assets = self.trading_system.get_top_assets(10)
            
            # Update GUI in the main thread
            self.root.after(0, self._update_assets_display, top_assets)
        except Exception as e:
            logging.error(f"Error refreshing assets: {e}")
    
    def _update_assets_display(self, top_assets):
        """Update the assets display in the GUI"""
        self.assets_text.delete(1.0, tk.END)
        
        if top_assets:
            for asset in top_assets:
                line = f"{asset['symbol']}: Score={asset['total_score']:.3f}, Volatility={asset['volatility']:.3f}\n"
                self.assets_text.insert(tk.END, line)
        else:
            self.assets_text.insert(tk.END, "No assets available or error occurred")
    
    def show_opportunities(self):
        """Show current trading opportunities"""
        opportunities = self.trading_system.trade_manager.scan_markets()
        
        if opportunities:
            opp_text = "Current Trading Opportunities:\n\n"
            for opp in opportunities[:10]:  # Show top 10
                opp_text += f"{opp['direction'].upper()} {opp['symbol']}\n"
                opp_text += f"  Entry: ${opp['entry_price']:.4f}\n"
                opp_text += f"  SL: ${opp['stop_loss']:.4f}, TP: ${opp['take_profit']:.4f}\n"
                opp_text += f"  Confidence: {opp['confidence']:.2f}\n\n"
            
            # Show in a new window
            opp_window = tk.Toplevel(self.root)
            opp_window.title("Trading Opportunities")
            opp_window.geometry("500x400")
            
            text_widget = scrolledtext.ScrolledText(opp_window)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, opp_text)
        else:
            messagebox.showinfo("Info", "No current trading opportunities found.")
    
    def execute_selected(self):
        """Execute selected trading opportunity (placeholder)"""
        messagebox.showinfo("Info", "Execute selected is a placeholder. In a real system, this would execute the selected trade.")
    
    def update_status(self):
        """Update system status display"""
        if hasattr(self.trading_system, 'get_system_status'):
            try:
                status = self.trading_system.get_system_status()
                
                # Update status labels
                running_text = "Yes" if status.get('is_running', False) else "No"
                self.status_labels['running'].config(text=running_text)
                
                capital = status.get('available_capital', 0)
                self.status_labels['capital'].config(text=f"${capital:.2f}")
                
                mode = status.get('current_mode', 'N/A')
                self.status_labels['mode'].config(text=mode)
                
                positions = status.get('active_positions', 0)
                self.status_labels['positions'].config(text=str(positions))
            except Exception as e:
                logging.error(f"Error updating status: {e}")
        
        # Schedule next update
        self.root.after(2000, self.update_status)  # Update every 2 seconds


def run_gui():
    """Run the GUI application"""
    root = tk.Tk()
    app = TradingGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.trading_system.is_running:
            app.trading_system.stop_system()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    run_gui()