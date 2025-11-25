"""
Configuration module for BingX API
Contains API keys and configuration settings
"""

from typing import Dict, Optional

# Direct API credentials - update these with your actual keys
BINGX_API_KEY = "YOUR_API_KEY_HERE"
BINGX_SECRET = "YOUR_SECRET_HERE"
BINGX_MODE = "swap"  # Change to "spot" if you want to use spot trading


class Config:
    """Configuration class for BingX API settings"""
    
    def __init__(self):
        # Load API keys directly from this file
        self.API_KEY = BINGX_API_KEY
        self.SECRET_KEY = BINGX_SECRET
        self.MODE = BINGX_MODE  # Default to swap mode
        self.BASE_URL = 'https://open-api.bingx.com'
        
        # Rate limiting settings
        self.RATE_LIMIT_DELAY = 0.2  # 200ms delay between requests
        self.MAX_REQUESTS_PER_SECOND = 5
        
        # Timeout settings
        self.REQUEST_TIMEOUT = 30
        self.CONNECTION_TIMEOUT = 10
        
        # Logging settings
        self.LOG_LEVEL = 'INFO'
        self.LOG_FILE = 'bingx_api.log'
        
        # Demo mode flag
        self.DEMO_MODE = False

    def get_api_credentials(self) -> Dict[str, str]:
        """Return API credentials as dictionary"""
        return {
            'api_key': self.API_KEY,
            'secret_key': self.SECRET_KEY
        }

    def get_mode(self) -> str:
        """Return the trading mode"""
        return self.MODE

    def get_base_url(self) -> str:
        """Return the base API URL"""
        return self.BASE_URL

    def is_demo_mode(self) -> bool:
        """Check if running in demo mode"""
        return self.DEMO_MODE


# Global configuration instance
config = Config()