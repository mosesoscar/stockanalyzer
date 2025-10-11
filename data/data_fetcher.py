"""
Data fetching module for stock market data.
Handles yFinance and Financial Modeling Prep API calls.
"""

import yfinance as yf
import requests
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import streamlit as st
from config.settings import config


class DataFetcher:
    """Fetch stock data from multiple sources"""
    
    def __init__(self):
        self.fmp_api_key = config.FMP_API_KEY
        self.fmp_base_url = config.FMP_BASE_URL
    
    @staticmethod
    @st.cache_data(ttl=config.CACHE_TTL_SECONDS)
    def get_stock_history(ticker: str, period: str = "1y") -> pd.DataFrame:
        """
        Get historical stock data from yFinance
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            return df
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=config.CACHE_TTL_SECONDS)
    def get_stock_info(ticker: str) -> Dict:
        """
        Get stock info from yFinance
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with stock information
        """
        try:
            stock = yf.Ticker(ticker)
            return stock.info
        except Exception as e:
            st.error(f"Error fetching info for {ticker}: {str(e)}")
            return {}
    
    @st.cache_data(ttl=config.CACHE_TTL_SECONDS)
    def get_company_profile(_self, ticker: str) -> Optional[Dict]:
        """
        Get company profile from FMP
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with company information
        """
        if not _self.fmp_api_key:
            return None
        
        try:
            url = f"{_self.fmp_base_url}/profile/{ticker}"
            params = {'apikey': _self.fmp_api_key}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
        except Exception as e:
            st.warning(f"Could not fetch FMP profile for {ticker}: {str(e)}")
            return None
    
    @st.cache_data(ttl=config.CACHE_TTL_SECONDS)
    def get_key_metrics(_self, ticker: str) -> Optional[Dict]:
        """
        Get key financial metrics from FMP
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with key metrics
        """
        if not _self.fmp_api_key:
            return None
        
        try:
            url = f"{_self.fmp_base_url}/key-metrics/{ticker}"
            params = {'apikey': _self.fmp_api_key, 'limit': 1}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
        except Exception as e:
            st.warning(f"Could not fetch FMP metrics for {ticker}: {str(e)}")
            return None
    
    @st.cache_data(ttl=1800)
    def get_stock_news(_self, ticker: str, limit: int = 5) -> List[Dict]:
        """
        Get latest stock news from FMP
        
        Args:
            ticker: Stock ticker symbol
            limit: Number of news articles to fetch
        
        Returns:
            List of news articles
        """
        if not _self.fmp_api_key:
            return []
        
        try:
            url = f"{_self.fmp_base_url}/stock_news"
            params = {
                'tickers': ticker,
                'limit': limit,
                'apikey': _self.fmp_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            st.warning(f"Could not fetch news for {ticker}: {str(e)}")
            return []
    
    @st.cache_data(ttl=3600)
    def get_analyst_ratings(_self, ticker: str) -> Optional[Dict]:
        """
        Get analyst ratings from FMP
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with analyst ratings
        """
        if not _self.fmp_api_key:
            return None
        
        try:
            url = f"{_self.fmp_base_url}/grade/{ticker}"
            params = {'apikey': _self.fmp_api_key, 'limit': 10}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    ratings = {'buy': 0, 'hold': 0, 'sell': 0, 'recent': []}
                    for rating in data[:5]:
                        grade = rating.get('newGrade', '').lower()
                        if 'buy' in grade or 'outperform' in grade:
                            ratings['buy'] += 1
                        elif 'hold' in grade or 'neutral' in grade:
                            ratings['hold'] += 1
                        elif 'sell' in grade or 'underperform' in grade:
                            ratings['sell'] += 1
                        ratings['recent'].append(rating)
                    return ratings
            return None
        except Exception as e:
            st.warning(f"Could not fetch analyst ratings for {ticker}: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600)
    def get_earnings_calendar(_self, ticker: str) -> Optional[Dict]:
        """
        Get upcoming earnings date from FMP
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with earnings information
        """
        if not _self.fmp_api_key:
            return None
        
        try:
            url = f"{_self.fmp_base_url}/earnings-calendar"
            params = {
                'symbol': ticker,
                'apikey': _self.fmp_api_key
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            return None
        except Exception as e:
            st.warning(f"Could not fetch earnings calendar for {ticker}: {str(e)}")
            return None
    
    def get_comprehensive_data(self, ticker: str) -> Dict:
        """
        Get all available data for a stock
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Dictionary with all fetched data
        """
        return {
            'profile': self.get_company_profile(ticker),
            'metrics': self.get_key_metrics(ticker),
            'news': self.get_stock_news(ticker),
            'ratings': self.get_analyst_ratings(ticker),
            'earnings': self.get_earnings_calendar(ticker)
        }