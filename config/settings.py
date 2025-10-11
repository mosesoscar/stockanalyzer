"""
Configuration settings for the Stock Analyzer application.
Store your API keys here (use environment variables in production).
"""

import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # API Keys (use environment variables in production)
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY', None)
    FMP_API_KEY: Optional[str] = os.getenv('FMP_API_KEY', None)
    
    # API Endpoints
    FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
    
    # Cache Settings
    CACHE_TTL_MINUTES = 30
    CACHE_TTL_SECONDS = CACHE_TTL_MINUTES * 60
    
    # Analysis Settings
    DEFAULT_RISK_FREE_RATE = 0.045  # 4.5% (approximate US Treasury rate)
    
    # Technical Indicator Defaults
    SMA_SHORT_DEFAULT = 20
    SMA_LONG_DEFAULT = 50
    RSI_PERIOD_DEFAULT = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    # Stock Universe Size
    MAX_UNIVERSE_SIZE = 300
    
    # Gemini Settings
    GEMINI_MODEL = "gemini-1.5-flash"  # Use Flash for cost efficiency
    GEMINI_TEMPERATURE = 0.3  # Lower = more consistent
    GEMINI_MAX_TOKENS = 1000
    
    @classmethod
    def validate_keys(cls) -> dict:
        """Validate that required API keys are set"""
        return {
            'gemini': cls.GEMINI_API_KEY is not None,
            'fmp': cls.FMP_API_KEY is not None
        }
    
    @classmethod
    def get_missing_keys(cls) -> list:
        """Get list of missing API keys"""
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append('GEMINI_API_KEY')
        if not cls.FMP_API_KEY:
            missing.append('FMP_API_KEY')
        return missing


# For easy importing
config = Config()