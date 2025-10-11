"""
Technical analysis module for stock data.
Calculate indicators, support/resistance, and generate signals.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from config.settings import config


class TechnicalAnalyzer:
    """Perform technical analysis on stock data"""
    
    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return data['Close'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data['Close'].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, 
                      fast: int = 12, 
                      slow: int = 26, 
                      signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD"""
        ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, 
                                  period: int = 20, 
                                  std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    @staticmethod
    def find_support_resistance(data: pd.DataFrame, 
                                window: int = 20) -> Tuple[List[float], List[float]]:
        """
        Find support and resistance levels using local minima/maxima
        
        Args:
            data: DataFrame with price data
            window: Window size for finding local extrema
        
        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        if len(data) < window * 2:
            return [], []
        
        # Find local minima (support)
        lows = data['Low'].rolling(window=window, center=True).min()
        support = data[data['Low'] == lows]['Low'].unique()
        support = sorted(support)[-5:]  # Keep last 5 levels
        
        # Find local maxima (resistance)
        highs = data['High'].rolling(window=window, center=True).max()
        resistance = data[data['High'] == highs]['High'].unique()
        resistance = sorted(resistance)[-5:]  # Keep last 5 levels
        
        return list(support), list(resistance)
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range (for volatility)"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr
    
    def get_technical_summary(self, data: pd.DataFrame) -> Dict:
        """
        Get comprehensive technical analysis summary
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            Dictionary with all technical indicators and signals
        """
        if data.empty or len(data) < 50:
            return {'error': 'Insufficient data for technical analysis'}
        
        # Calculate all indicators
        data['SMA_20'] = self.calculate_sma(data, 20)
        data['SMA_50'] = self.calculate_sma(data, 50)
        data['SMA_200'] = self.calculate_sma(data, 200)
        data['RSI'] = self.calculate_rsi(data, 14)
        data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = self.calculate_macd(data)
        data['BB_Upper'], data['BB_Middle'], data['BB_Lower'] = self.calculate_bollinger_bands(data)
        data['ATR'] = self.calculate_atr(data)
        
        # Get latest values
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) > 1 else latest
        
        # Find support and resistance
        support, resistance = self.find_support_resistance(data)
        
        # Determine trend
        trend = self._determine_trend(latest, data)
        
        # Generate signals
        signals = self._generate_signals(latest, prev, data)
        
        # Calculate volume analysis
        volume_analysis = self._analyze_volume(data)
        
        return {
            'current_price': float(latest['Close']),
            'previous_close': float(prev['Close']),
            'change_pct': float(((latest['Close'] - prev['Close']) / prev['Close']) * 100),
            'volume': int(latest['Volume']),
            'volume_analysis': volume_analysis,
            'trend': trend,
            'indicators': {
                'rsi': float(latest['RSI']) if pd.notna(latest['RSI']) else None,
                'rsi_signal': self._interpret_rsi(latest['RSI']),
                'macd': float(latest['MACD']) if pd.notna(latest['MACD']) else None,
                'macd_signal': float(latest['MACD_Signal']) if pd.notna(latest['MACD_Signal']) else None,
                'macd_histogram': float(latest['MACD_Hist']) if pd.notna(latest['MACD_Hist']) else None,
                'macd_interpretation': self._interpret_macd(latest, prev),
                'sma_20': float(latest['SMA_20']) if pd.notna(latest['SMA_20']) else None,
                'sma_50': float(latest['SMA_50']) if pd.notna(latest['SMA_50']) else None,
                'sma_200': float(latest['SMA_200']) if pd.notna(latest['SMA_200']) else None,
                'bb_upper': float(latest['BB_Upper']) if pd.notna(latest['BB_Upper']) else None,
                'bb_lower': float(latest['BB_Lower']) if pd.notna(latest['BB_Lower']) else None,
                'atr': float(latest['ATR']) if pd.notna(latest['ATR']) else None
            },
            'support_levels': [float(s) for s in support],
            'resistance_levels': [float(r) for r in resistance],
            'signals': signals,
            'volatility': self._calculate_volatility(data)
        }
    
    def _determine_trend(self, latest: pd.Series, data: pd.DataFrame) -> str:
        """Determine overall trend"""
        price = latest['Close']
        sma_20 = latest['SMA_20']
        sma_50 = latest['SMA_50']
        
        if pd.isna(sma_20) or pd.isna(sma_50):
            return 'Unknown'
        
        if price > sma_20 > sma_50:
            return 'Strong Uptrend'
        elif price > sma_20:
            return 'Uptrend'
        elif price < sma_20 < sma_50:
            return 'Strong Downtrend'
        elif price < sma_20:
            return 'Downtrend'
        else:
            return 'Sideways'
    
    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI value"""
        if pd.isna(rsi):
            return 'Unknown'
        if rsi > 70:
            return 'Overbought'
        elif rsi < 30:
            return 'Oversold'
        else:
            return 'Neutral'
    
    def _interpret_macd(self, latest: pd.Series, prev: pd.Series) -> str:
        """Interpret MACD signal"""
        macd = latest['MACD']
        signal = latest['MACD_Signal']
        prev_macd = prev['MACD']
        prev_signal = prev['MACD_Signal']
        
        if pd.isna(macd) or pd.isna(signal):
            return 'Unknown'
        
        # Check for crossover
        if prev_macd < prev_signal and macd > signal:
            return 'Bullish Crossover'
        elif prev_macd > prev_signal and macd < signal:
            return 'Bearish Crossover'
        elif macd > signal:
            return 'Bullish'
        else:
            return 'Bearish'
    
    def _generate_signals(self, latest: pd.Series, prev: pd.Series, data: pd.DataFrame) -> Dict:
        """Generate trading signals"""
        signals = {
            'overall': 'NEUTRAL',
            'strength': 0,  # -10 to +10
            'reasons': []
        }
        
        score = 0
        
        # RSI signals
        rsi = latest['RSI']
        if not pd.isna(rsi):
            if rsi > 70:
                score -= 2
                signals['reasons'].append('RSI Overbought')
            elif rsi < 30:
                score += 2
                signals['reasons'].append('RSI Oversold')
        
        # MACD signals
        macd_interp = self._interpret_macd(latest, prev)
        if macd_interp == 'Bullish Crossover':
            score += 3
            signals['reasons'].append('MACD Bullish Crossover')
        elif macd_interp == 'Bearish Crossover':
            score -= 3
            signals['reasons'].append('MACD Bearish Crossover')
        
        # Moving average signals
        price = latest['Close']
        if not pd.isna(latest['SMA_20']) and not pd.isna(latest['SMA_50']):
            if price > latest['SMA_20'] > latest['SMA_50']:
                score += 2
                signals['reasons'].append('Price Above Key MAs')
            elif price < latest['SMA_20'] < latest['SMA_50']:
                score -= 2
                signals['reasons'].append('Price Below Key MAs')
        
        # Set overall signal
        signals['strength'] = score
        if score >= 3:
            signals['overall'] = 'STRONG BUY'
        elif score >= 1:
            signals['overall'] = 'BUY'
        elif score <= -3:
            signals['overall'] = 'STRONG SELL'
        elif score <= -1:
            signals['overall'] = 'SELL'
        
        return signals
    
    def _analyze_volume(self, data: pd.DataFrame) -> Dict:
        """Analyze volume patterns"""
        if len(data) < 20:
            return {'status': 'Insufficient data'}
        
        current_volume = data['Volume'].iloc[-1]
        avg_volume_20 = data['Volume'].iloc[-20:].mean()
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
        
        return {
            'current': int(current_volume),
            'average_20d': int(avg_volume_20),
            'ratio': float(volume_ratio),
            'status': 'High' if volume_ratio > 1.5 else 'Normal' if volume_ratio > 0.5 else 'Low'
        }
    
    def _calculate_volatility(self, data: pd.DataFrame) -> Dict:
        """Calculate volatility metrics"""
        if len(data) < 20:
            return {'status': 'Insufficient data'}
        
        returns = data['Close'].pct_change()
        volatility_20d = returns.iloc[-20:].std() * np.sqrt(252) * 100  # Annualized
        
        return {
            'annualized_20d': float(volatility_20d),
            'status': 'High' if volatility_20d > 40 else 'Moderate' if volatility_20d > 20 else 'Low'
        }