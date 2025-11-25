"""
Configuration module for BingX API
Contains API keys and configuration settings
"""

import os
from typing import Dict, Optional


class Config:
    """Configuration class for BingX API settings"""
    
    def __init__(self):
        # Load API keys from environment variables or use defaults
        self.API_KEY = os.getenv('BINGX_API_KEY', 'l6aSBNGk0qIWFi03rQgQjFOxz71APDse4qxUw3I05nI7cxZybzbwODxh1aDDLDN8CC7iEye5CH8gr1iOWdA')
        self.SECRET_KEY = os.getenv('BINGX_SECRET_KEY', 'NdqT8ExENJ28GOvFG7hUl3mcHa6GrCtIFyiNxSAsNe8Jk6SbchAt27uCf3v9SLIbQVqoLcKKl2kcA3Ng')
        self.BASE_URL = os.getenv('BINGX_BASE_URL', 'https://open-api.bingx.com')
        
        # Rate limiting settings
        self.RATE_LIMIT_DELAY = float(os.getenv('RATE_LIMIT_DELAY', '0.2'))  # 200ms delay between requests
        self.MAX_REQUESTS_PER_SECOND = int(os.getenv('MAX_REQUESTS_PER_SECOND', '5'))
        
        # Timeout settings
        self.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.CONNECTION_TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', '10'))
        
        # Logging settings
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'bingx_api.log')
        
        # Demo mode flag
        self.DEMO_MODE = os.getenv('BINGX_DEMO_MODE', 'false').lower() == 'true'

    def get_api_credentials(self) -> Dict[str, str]:
        """Return API credentials as dictionary"""
        return {
            'api_key': self.API_KEY,
            'secret_key': self.SECRET_KEY
        }

    def get_base_url(self) -> str:
        """Return the base API URL"""
        return self.BASE_URL

    def is_demo_mode(self) -> bool:
        """Check if running in demo mode"""
        return self.DEMO_MODE


# Global configuration instance
config = Config()