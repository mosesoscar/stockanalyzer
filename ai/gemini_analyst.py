"""
Gemini AI integration for stock analysis.
Combines technical and fundamental analysis for AI-powered recommendations.
"""

import google.generativeai as genai
from typing import Dict, Optional
import json
import streamlit as st
from config.settings import config


class GeminiAnalyst:
    """AI-powered stock analyst using Google Gemini"""
    
    def __init__(self):
        """Initialize Gemini with API key"""
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name=config.GEMINI_MODEL,
                generation_config={
                    'temperature': config.GEMINI_TEMPERATURE,
                    'max_output_tokens': config.GEMINI_MAX_TOKENS,
                }
            )
            self.enabled = True
        else:
            self.enabled = False
    
    def analyze_stock(self, 
                     ticker: str,
                     technical_data: Dict,
                     fundamental_data: Dict) -> Optional[Dict]:
        """
        Get AI-powered stock analysis and recommendations
        
        Args:
            ticker: Stock ticker symbol
            technical_data: Technical analysis results
            fundamental_data: Fundamental analysis results
        
        Returns:
            Dictionary with AI recommendations or None if disabled
        """
        if not self.enabled:
            return None
        
        try:
            # Build comprehensive prompt
            prompt = self._build_analysis_prompt(ticker, technical_data, fundamental_data)
            
            # Get Gemini's analysis
            response = self.model.generate_content(prompt)
            
            # Parse response
            analysis = self._parse_response(response.text)
            
            return analysis
            
        except Exception as e:
            st.error(f"Gemini analysis error: {str(e)}")
            return None
    
    def _build_analysis_prompt(self, 
                               ticker: str,
                               technical: Dict,
                               fundamental: Dict) -> str:
        """Build detailed prompt for Gemini"""
        
        # Extract key data
        current_price = technical.get('current_price', 0)
        trend = technical.get('trend', 'Unknown')
        rsi = technical['indicators'].get('rsi')
        macd_interp = technical['indicators'].get('macd_interpretation')
        signals = technical.get('signals', {})
        support = technical.get('support_levels', [])
        resistance = technical.get('resistance_levels', [])
        volume_status = technical.get('volume_analysis', {}).get('status', 'Unknown')
        
        # Fundamental data
        profile = fundamental.get('profile', {})
        metrics = fundamental.get('metrics', {})
        ratings = fundamental.get('ratings', {})
        news = fundamental.get('news', {})
        
        prompt = f"""You are an expert stock analyst. Analyze {ticker} and provide actionable investment recommendations.

TECHNICAL ANALYSIS:
- Current Price: ${current_price:.2f}
- Trend: {trend}
- RSI: {rsi:.1f if rsi else 'N/A'} ({technical['indicators'].get('rsi_signal', 'Unknown')})
- MACD: {macd_interp}
- Volume: {volume_status}
- Support Levels: {', '.join([f'${s:.2f}' for s in support[:3]]) if support else 'N/A'}
- Resistance Levels: {', '.join([f'${r:.2f}' for r in resistance[:3]]) if resistance else 'N/A'}
- Technical Signal: {signals.get('overall', 'NEUTRAL')} (Strength: {signals.get('strength', 0)}/10)

FUNDAMENTAL ANALYSIS:
"""
        
        # Add fundamental data if available
        if profile.get('available'):
            prompt += f"""
- Company: {profile.get('company_name', 'N/A')}
- Sector: {profile.get('sector', 'N/A')} | Industry: {profile.get('industry', 'N/A')}
- Market Cap: {profile.get('market_cap_formatted', 'N/A')}
"""
        
        if metrics.get('available'):
            val = metrics.get('valuation', {})
            prof = metrics.get('profitability', {})
            health = metrics.get('financial_health', {})
            
            prompt += f"""
- P/E Ratio: {val.get('pe_ratio', 'N/A')} ({val.get('pe_interpretation', 'N/A')})
- P/B Ratio: {val.get('pb_ratio', 'N/A')} ({val.get('pb_interpretation', 'N/A')})
- ROE: {prof.get('roe', 'N/A')}% ({prof.get('roe_interpretation', 'N/A')})
- Debt/Equity: {health.get('debt_to_equity', 'N/A')} ({health.get('debt_interpretation', 'N/A')})
"""
        
        if ratings.get('available'):
            prompt += f"""
- Analyst Consensus: {ratings.get('consensus', 'N/A')} 
  (Buy: {ratings.get('buy', 0)}, Hold: {ratings.get('hold', 0)}, Sell: {ratings.get('sell', 0)})
"""
        
        if news.get('available') and news.get('articles'):
            prompt += f"\n- Recent News: {news.get('count', 0)} articles in past week\n"
            for article in news['articles'][:2]:
                prompt += f"  • {article.get('title', 'N/A')}\n"
        
        prompt += f"""

INSTRUCTIONS:
1. Use web search to find the LATEST information about {ticker}:
   - Breaking news from the past 24-48 hours
   - Recent earnings reports or guidance
   - Major announcements or developments
   - Industry trends affecting the company

2. Combine technical analysis, fundamental analysis, and latest news to provide:
   
YOUR ANALYSIS (Provide as valid JSON):
{{
  "recommendation": "BUY" | "HOLD" | "SELL",
  "confidence": 1-10,
  "reasoning": "2-3 sentences explaining your recommendation based on technical + fundamental + news",
  "entry_point": {{
    "price": specific dollar amount,
    "rationale": "why this price?"
  }},
  "stop_loss": {{
    "price": specific dollar amount,
    "rationale": "risk management reasoning"
  }},
  "target_price": {{
    "price_3month": specific dollar amount,
    "upside_potential": percentage,
    "rationale": "basis for target"
  }},
  "risk_factors": [
    "Risk 1",
    "Risk 2",
    "Risk 3"
  ],
  "catalysts": [
    "Positive catalyst 1",
    "Positive catalyst 2"
  ]
}}

IMPORTANT: 
- Provide ONLY valid JSON, no additional text
- Be specific with prices (don't use ranges)
- Base stop loss on technical support levels or ATR
- Consider both short-term technicals and long-term fundamentals
- Factor in recent news and market sentiment
"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini's JSON response"""
        try:
            # Try to extract JSON from response
            # Sometimes Gemini adds markdown formatting
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = response_text.strip()
            
            # Parse JSON
            analysis = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['recommendation', 'confidence', 'reasoning']
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse Gemini response: {str(e)}")
            # Return fallback structure
            return {
                'recommendation': 'HOLD',
                'confidence': 5,
                'reasoning': 'Unable to generate detailed analysis. Please try again.',
                'entry_point': {'price': None, 'rationale': 'N/A'},
                'stop_loss': {'price': None, 'rationale': 'N/A'},
                'target_price': {'price_3month': None, 'upside_potential': None, 'rationale': 'N/A'},
                'risk_factors': ['Analysis unavailable'],
                'catalysts': ['Analysis unavailable']
            }
        except Exception as e:
            st.error(f"Error processing Gemini response: {str(e)}")
            return None
    
    def get_quick_insight(self, ticker: str, technical_signal: str) -> Optional[str]:
        """
        Get a quick one-sentence insight about the stock
        
        Args:
            ticker: Stock ticker
            technical_signal: Quick technical signal (BUY/SELL/HOLD)
        
        Returns:
            Short insight string
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""In one sentence, what's the key thing investors should know about {ticker} right now? 
Technical signal shows: {technical_signal}. 
Use web search to find latest news. Keep it under 25 words."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return None