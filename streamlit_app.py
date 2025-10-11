"""
Main Streamlit application file.
Clean UI that calls modular components.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.settings import config
from data.data_fetcher import DataFetcher
from analysis.technical import TechnicalAnalyzer
from analysis.fundamental import FundamentalAnalyzer
from ai.gemini_analyst import GeminiAnalyst
from utils.helpers import (
    display_api_status, display_recommendation_card,
    create_price_chart, create_rsi_chart, create_macd_chart,
    get_signal_emoji, get_signal_color
)

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize components
data_fetcher = DataFetcher()
technical_analyzer = TechnicalAnalyzer()
fundamental_analyzer = FundamentalAnalyzer()
gemini_analyst = GeminiAnalyst()

# Title
st.title("📈 AI-Powered Stock Analysis Dashboard")
st.markdown("*Real-time data with technical indicators, fundamental analysis, and AI recommendations*")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Mode", ["🔍 Discover Stocks", "📊 Analyze Stock", "🤖 AI Insights"])

# Display API status
display_api_status()

# ============= DISCOVER STOCKS PAGE =============
if page == "🔍 Discover Stocks":
    st.header("🔥 Discover Stocks")
    st.info("Discovery mode from your original implementation. Keep your existing discovery code here or import it.")
    
    st.markdown("""
    This page will contain your stock discovery features:
    - Dynamic categories (Top Gainers, Losers, etc.)
    - Static curated lists
    - Filters and sorting
    
    You can keep your existing discovery code here since it's already well-built!
    """)

# ============= ANALYZE STOCK PAGE =============
elif page == "📊 Analyze Stock":
    st.header("📊 Deep Stock Analysis")
    
    # Stock input
    col1, col2 = st.columns([3, 1])
    with col1:
        ticker = st.text_input("Enter Stock Ticker", value="AAPL", key="ticker_input").upper()
    with col2:
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)
    
    analyze_button = st.button("🔍 Analyze Stock", type="primary", use_container_width=True)
    
    if analyze_button and ticker:
        with st.spinner(f"Analyzing {ticker}..."):
            
            # Fetch data
            df = data_fetcher.get_stock_history(ticker, period)
            info = data_fetcher.get_stock_info(ticker)
            
            if df.empty:
                st.error(f"Could not fetch data for {ticker}")
                st.stop()
            
            # Technical Analysis
            st.subheader("📈 Technical Analysis")
            technical_data = technical_analyzer.get_technical_summary(df)
            
            if 'error' in technical_data:
                st.error(technical_data['error'])
                st.stop()
            
            # Display current metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                price = technical_data['current_price']
                change = technical_data['change_pct']
                st.metric("Current Price", f"${price:.2f}", f"{change:+.2f}%")
            
            with col2:
                rsi = technical_data['indicators']['rsi']
                rsi_signal = technical_data['indicators']['rsi_signal']
                st.metric("RSI", f"{rsi:.1f}" if rsi else "N/A", rsi_signal)
            
            with col3:
                signal = technical_data['signals']['overall']
                emoji = get_signal_emoji(signal)
                st.metric("Technical Signal", f"{emoji} {signal}")
            
            with col4:
                vol_status = technical_data['volume_analysis']['status']
                vol_ratio = technical_data['volume_analysis']['ratio']
                st.metric("Volume", vol_status, f"{vol_ratio:.2f}x")
            
            # Simple insights
            st.markdown("### 💡 Quick Insights")
            trend = technical_data['trend']
            st.info(f"**Trend:** {trend}")
            
            macd_interp = technical_data['indicators']['macd_interpretation']
            st.info(f"**MACD:** {macd_interp}")
            
            # Support and Resistance
            col1, col2 = st.columns(2)
            with col1:
                support = technical_data.get('support_levels', [])
                if support:
                    st.markdown("**📉 Support Levels:**")
                    for level in support[:3]:
                        st.write(f"- ${level:.2f}")
            
            with col2:
                resistance = technical_data.get('resistance_levels', [])
                if resistance:
                    st.markdown("**📈 Resistance Levels:**")
                    for level in resistance[:3]:
                        st.write(f"- ${level:.2f}")
            
            # Charts
            st.markdown("---")
            st.subheader("📊 Interactive Charts")
            
            # Calculate indicators for charts
            df['SMA_20'] = technical_analyzer.calculate_sma(df, 20)
            df['SMA_50'] = technical_analyzer.calculate_sma(df, 50)
            df['RSI'] = technical_analyzer.calculate_rsi(df, 14)
            df['MACD'], df['Signal'], df['Histogram'] = technical_analyzer.calculate_macd(df)
            df_clean = df.dropna()
            
            # Price chart
            fig1 = create_price_chart(df_clean, df_clean['SMA_20'], df_clean['SMA_50'])
            st.plotly_chart(fig1, use_container_width=True)
            
            # RSI chart
            fig2 = create_rsi_chart(df_clean, df_clean['RSI'])
            st.plotly_chart(fig2, use_container_width=True)
            
            # MACD chart
            fig3 = create_macd_chart(df_clean, df_clean['MACD'], df_clean['Signal'], df_clean['Histogram'])
            st.plotly_chart(fig3, use_container_width=True)
            
            # Fundamental Analysis (if FMP key available)
            st.markdown("---")
            st.subheader("💼 Fundamental Analysis")
            
            if config.FMP_API_KEY:
                with st.spinner("Fetching fundamental data..."):
                    fmp_data = data_fetcher.get_comprehensive_data(ticker)
                    fundamental_data = fundamental_analyzer.get_fundamental_summary(fmp_data)
                
                # Display company profile
                profile = fundamental_data.get('profile', {})
                if profile.get('available'):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Company", profile['company_name'])
                        st.caption(f"{profile['sector']} - {profile['industry']}")
                    with col2:
                        st.metric("Market Cap", profile['market_cap_formatted'])
                    with col3:
                        st.metric("Exchange", profile['exchange'])
                
                # Display metrics
                metrics = fundamental_data.get('metrics', {})
                if metrics.get('available'):
                    st.markdown("### 📊 Key Metrics")
                    col1, col2, col3 = st.columns(3)
                    
                    val = metrics.get('valuation', {})
                    with col1:
                        pe = val.get('pe_ratio')
                        if pe:
                            st.metric("P/E Ratio", f"{pe:.2f}", val.get('pe_interpretation'))
                    
                    prof = metrics.get('profitability', {})
                    with col2:
                        roe = prof.get('roe')
                        if roe:
                            st.metric("ROE", f"{roe:.2f}%", prof.get('roe_interpretation'))
                    
                    health = metrics.get('financial_health', {})
                    with col3:
                        debt = health.get('debt_to_equity')
                        if debt:
                            st.metric("Debt/Equity", f"{debt:.2f}", health.get('debt_interpretation'))
                
                # Display analyst ratings
                ratings = fundamental_data.get('ratings', {})
                if ratings.get('available'):
                    st.markdown("### 👥 Analyst Ratings")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Consensus", ratings['consensus'])
                    with col2:
                        st.metric("Buy", ratings['buy'])
                    with col3:
                        st.metric("Hold", ratings['hold'])
                    with col4:
                        st.metric("Sell", ratings['sell'])
                
                # Display recent news
                news = fundamental_data.get('news', {})
                if news.get('available'):
                    st.markdown("### 📰 Recent News")
                    for article in news['articles'][:3]:
                        st.markdown(f"**[{article['title']}]({article['url']})**")
                        st.caption(f"{article['site']} - {article['published_date']}")
            else:
                st.warning("⚠️ FMP API key not configured. Set FMP_API_KEY in config/settings.py for fundamental analysis.")
                fundamental_data = {'profile': {}, 'metrics': {}, 'news': {}, 'ratings': {}}
            
            # AI Analysis Button
            st.markdown("---")
            if st.button("🤖 Get AI-Powered Recommendation", type="primary", use_container_width=True):
                if not gemini_analyst.enabled:
                    st.error("⚠️ Gemini API key not configured. Set GEMINI_API_KEY in config/settings.py")
                else:
                    with st.spinner("AI is analyzing the stock... This may take 10-15 seconds..."):
                        ai_analysis = gemini_analyst.analyze_stock(ticker, technical_data, fundamental_data)
                        
                        if ai_analysis:
                            st.session_state['ai_analysis'] = ai_analysis
                            st.rerun()
            
            # Display AI analysis if available
            if 'ai_analysis' in st.session_state:
                st.markdown("---")
                st.subheader("🤖 AI-Powered Recommendation")
                display_recommendation_card(st.session_state['ai_analysis'])
                
                if st.button("Clear AI Analysis"):
                    del st.session_state['ai_analysis']
                    st.rerun()

# ============= AI INSIGHTS PAGE =============
elif page == "🤖 AI Insights":
    st.header("🤖 AI-Powered Stock Insights")
    
    if not gemini_analyst.enabled:
        st.error("⚠️ Gemini API key not configured")
        st.markdown("""
        To enable AI insights:
        1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Set it in `config/settings.py` or as environment variable `GEMINI_API_KEY`
        """)
        st.stop()
    
    st.markdown("""
    This page provides AI-powered insights across multiple stocks.
    
    ### Features:
    - Quick market sentiment analysis
    - Comparative stock analysis
    - Sector trends and recommendations
    - Portfolio suggestions
    """)
    
    # Quick Insight Tool
    st.subheader("💡 Quick Stock Insight")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        insight_ticker = st.text_input("Enter ticker for quick insight", "AAPL", key="insight_ticker").upper()
    with col2:
        if st.button("Get Insight", type="primary"):
            if insight_ticker:
                with st.spinner("Getting AI insight..."):
                    # Get quick technical signal
                    df = data_fetcher.get_stock_history(insight_ticker, "1mo")
                    if not df.empty:
                        tech_data = technical_analyzer.get_technical_summary(df)
                        signal = tech_data['signals']['overall']
                        
                        insight = gemini_analyst.get_quick_insight(insight_ticker, signal)
                        if insight:
                            st.info(f"**{insight_ticker}:** {insight}")
                        else:
                            st.warning("Could not generate insight")
    
    st.markdown("---")
    
    # Batch Analysis
    st.subheader("📊 Compare Multiple Stocks")
    tickers_input = st.text_input("Enter tickers (comma-separated)", "AAPL, MSFT, GOOGL")
    
    if st.button("Compare Stocks"):
        tickers = [t.strip().upper() for t in tickers_input.split(',')]
        
        if len(tickers) > 5:
            st.warning("Please limit to 5 stocks for comparison")
        else:
            comparison_data = []
            
            for ticker in tickers:
                with st.spinner(f"Analyzing {ticker}..."):
                    df = data_fetcher.get_stock_history(ticker, "3mo")
                    if not df.empty:
                        tech = technical_analyzer.get_technical_summary(df)
                        comparison_data.append({
                            'Ticker': ticker,
                            'Price': f"${tech['current_price']:.2f}",
                            'Change %': f"{tech['change_pct']:+.2f}%",
                            'Signal': tech['signals']['overall'],
                            'RSI': f"{tech['indicators']['rsi']:.1f}" if tech['indicators']['rsi'] else 'N/A',
                            'Trend': tech['trend']
                        })
            
            if comparison_data:
                import pandas as pd
                df_compare = pd.DataFrame(comparison_data)
                st.dataframe(df_compare, use_container_width=True)

# Footer
st.markdown("---")
st.caption(f"📊 Stock Analysis Dashboard | Data: Yahoo Finance & FMP | AI: Google Gemini")
st.caption("⚠️ Disclaimer: For educational purposes only. Not financial advice. Always do your own research.")