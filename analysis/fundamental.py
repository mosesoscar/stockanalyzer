"""
Fundamental analysis module.
Process FMP data and generate fundamental insights.
"""

from typing import Dict, Optional, List
from datetime import datetime


class FundamentalAnalyzer:
    """Analyze fundamental data from FMP"""
    
    @staticmethod
    def analyze_profile(profile: Optional[Dict]) -> Dict:
        """
        Analyze company profile data
        
        Args:
            profile: Company profile from FMP
        
        Returns:
            Dictionary with analyzed profile data
        """
        if not profile:
            return {'available': False}
        
        return {
            'available': True,
            'company_name': profile.get('companyName', 'N/A'),
            'sector': profile.get('sector', 'N/A'),
            'industry': profile.get('industry', 'N/A'),
            'market_cap': profile.get('mktCap', 0),
            'market_cap_formatted': FundamentalAnalyzer._format_market_cap(profile.get('mktCap', 0)),
            'description': profile.get('description', '')[:200] + '...' if profile.get('description') else 'N/A',
            'ceo': profile.get('ceo', 'N/A'),
            'website': profile.get('website', 'N/A'),
            'exchange': profile.get('exchangeShortName', 'N/A'),
            'country': profile.get('country', 'N/A'),
            'employees': profile.get('fullTimeEmployees', 'N/A')
        }
    
    @staticmethod
    def analyze_metrics(metrics: Optional[Dict]) -> Dict:
        """
        Analyze key financial metrics
        
        Args:
            metrics: Key metrics from FMP
        
        Returns:
            Dictionary with analyzed metrics
        """
        if not metrics:
            return {'available': False}
        
        # Extract key ratios
        pe_ratio = metrics.get('peRatio')
        pb_ratio = metrics.get('pbRatio')
        debt_to_equity = metrics.get('debtToEquity')
        roe = metrics.get('roe')
        roa = metrics.get('roa')
        current_ratio = metrics.get('currentRatio')
        
        return {
            'available': True,
            'valuation': {
                'pe_ratio': float(pe_ratio) if pe_ratio else None,
                'pe_interpretation': FundamentalAnalyzer._interpret_pe(pe_ratio),
                'pb_ratio': float(pb_ratio) if pb_ratio else None,
                'pb_interpretation': FundamentalAnalyzer._interpret_pb(pb_ratio)
            },
            'profitability': {
                'roe': float(roe * 100) if roe else None,
                'roe_interpretation': FundamentalAnalyzer._interpret_roe(roe),
                'roa': float(roa * 100) if roa else None
            },
            'financial_health': {
                'debt_to_equity': float(debt_to_equity) if debt_to_equity else None,
                'debt_interpretation': FundamentalAnalyzer._interpret_debt(debt_to_equity),
                'current_ratio': float(current_ratio) if current_ratio else None,
                'liquidity_interpretation': FundamentalAnalyzer._interpret_liquidity(current_ratio)
            }
        }
    
    @staticmethod
    def analyze_news(news: List[Dict]) -> Dict:
        """
        Analyze news sentiment and recency
        
        Args:
            news: List of news articles from FMP
        
        Returns:
            Dictionary with news analysis
        """
        if not news:
            return {'available': False, 'articles': []}
        
        # Get recent articles (last 5)
        recent_news = []
        for article in news[:5]:
            recent_news.append({
                'title': article.get('title', 'N/A'),
                'published_date': article.get('publishedDate', 'N/A'),
                'site': article.get('site', 'N/A'),
                'url': article.get('url', '#')
            })
        
        return {
            'available': True,
            'count': len(news),
            'articles': recent_news,
            'latest_date': news[0].get('publishedDate', 'N/A') if news else 'N/A'
        }
    
    @staticmethod
    def analyze_ratings(ratings: Optional[Dict]) -> Dict:
        """
        Analyze analyst ratings
        
        Args:
            ratings: Analyst ratings from FMP
        
        Returns:
            Dictionary with rating analysis
        """
        if not ratings:
            return {'available': False}
        
        buy = ratings.get('buy', 0)
        hold = ratings.get('hold', 0)
        sell = ratings.get('sell', 0)
        total = buy + hold + sell
        
        if total == 0:
            return {'available': False}
        
        # Calculate consensus
        if buy / total > 0.6:
            consensus = 'Strong Buy'
        elif buy / total > 0.4:
            consensus = 'Buy'
        elif sell / total > 0.6:
            consensus = 'Strong Sell'
        elif sell / total > 0.4:
            consensus = 'Sell'
        else:
            consensus = 'Hold'
        
        return {
            'available': True,
            'buy': buy,
            'hold': hold,
            'sell': sell,
            'total': total,
            'consensus': consensus,
            'buy_percentage': round((buy / total) * 100, 1),
            'recent_ratings': ratings.get('recent', [])[:3]
        }
    
    @staticmethod
    def analyze_earnings(earnings: Optional[Dict]) -> Dict:
        """
        Analyze earnings information
        
        Args:
            earnings: Earnings calendar data from FMP
        
        Returns:
            Dictionary with earnings analysis
        """
        if not earnings:
            return {'available': False}
        
        return {
            'available': True,
            'date': earnings.get('date', 'N/A'),
            'eps_estimated': earnings.get('epsEstimated'),
            'revenue_estimated': earnings.get('revenueEstimated')
        }
    
    @staticmethod
    def _format_market_cap(market_cap: float) -> str:
        """Format market cap in readable form"""
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
        else:
            return f"${market_cap:,.0f}"
    
    @staticmethod
    def _interpret_pe(pe: Optional[float]) -> str:
        """Interpret P/E ratio"""
        if not pe or pe <= 0:
            return 'N/A'
        if pe < 15:
            return 'Undervalued'
        elif pe < 25:
            return 'Fair Value'
        else:
            return 'Overvalued'
    
    @staticmethod
    def _interpret_pb(pb: Optional[float]) -> str:
        """Interpret P/B ratio"""
        if not pb or pb <= 0:
            return 'N/A'
        if pb < 1:
            return 'Undervalued'
        elif pb < 3:
            return 'Fair Value'
        else:
            return 'Overvalued'
    
    @staticmethod
    def _interpret_roe(roe: Optional[float]) -> str:
        """Interpret ROE"""
        if not roe:
            return 'N/A'
        roe_pct = roe * 100
        if roe_pct > 20:
            return 'Excellent'
        elif roe_pct > 15:
            return 'Good'
        elif roe_pct > 10:
            return 'Average'
        else:
            return 'Poor'
    
    @staticmethod
    def _interpret_debt(debt_to_equity: Optional[float]) -> str:
        """Interpret debt to equity ratio"""
        if not debt_to_equity:
            return 'N/A'
        if debt_to_equity < 0.5:
            return 'Low Debt'
        elif debt_to_equity < 1.5:
            return 'Moderate Debt'
        else:
            return 'High Debt'
    
    @staticmethod
    def _interpret_liquidity(current_ratio: Optional[float]) -> str:
        """Interpret current ratio"""
        if not current_ratio:
            return 'N/A'
        if current_ratio > 2:
            return 'Strong Liquidity'
        elif current_ratio > 1:
            return 'Adequate Liquidity'
        else:
            return 'Weak Liquidity'
    
    def get_fundamental_summary(self, fmp_data: Dict) -> Dict:
        """
        Get comprehensive fundamental analysis
        
        Args:
            fmp_data: Dictionary with all FMP data
        
        Returns:
            Complete fundamental analysis
        """
        return {
            'profile': self.analyze_profile(fmp_data.get('profile')),
            'metrics': self.analyze_metrics(fmp_data.get('metrics')),
            'news': self.analyze_news(fmp_data.get('news')),
            'ratings': self.analyze_ratings(fmp_data.get('ratings')),
            'earnings': self.analyze_earnings(fmp_data.get('earnings'))
        }