import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📈 Stock Analysis Dashboard")
st.markdown("*Real-time stock data with technical indicators and stock discovery*")

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Mode", ["🔍 Discover Stocks", "📊 Analyze Stock"])

# Stock universe for real-time calculations (~300 most liquid stocks)
STOCK_UNIVERSE = [
    # Mega Cap Tech
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'ORCL', 'AMD',
    'CRM', 'ADBE', 'CSCO', 'ACN', 'NFLX', 'INTC', 'QCOM', 'TXN', 'INTU', 'IBM',
    # Financial Services
    'BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'SCHW', 'BLK', 'C', 'AXP',
    'SPGI', 'CB', 'PGR', 'MMC', 'USB', 'PNC', 'BK', 'TFC',
    # Healthcare
    'UNH', 'LLY', 'JNJ', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY',
    'AMGN', 'GILD', 'CVS', 'CI', 'ISRG', 'REGN', 'VRTX', 'ZTS', 'BSX', 'ELV',
    # Consumer
    'WMT', 'HD', 'COST', 'PG', 'KO', 'PEP', 'MCD', 'NKE', 'SBUX', 'TGT',
    'LOW', 'TJX', 'EL', 'MDLZ', 'CL', 'KMB', 'GIS', 'HSY', 'CLX', 'SJM',
    # Industrial
    'BA', 'CAT', 'HON', 'UPS', 'RTX', 'GE', 'LMT', 'DE', 'MMM', 'UNP',
    'ADP', 'ITW', 'EMR', 'FDX', 'NSC', 'CSX', 'WM', 'PH', 'ETN', 'GD',
    # Energy
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HAL',
    'KMI', 'WMB', 'HES', 'BKR', 'FANG', 'DVN', 'MRO', 'APA', 'OVV', 'CTRA',
    # Communication Services
    'DIS', 'CMCSA', 'NFLX', 'T', 'VZ', 'TMUS', 'WBD', 'EA', 'TTWO', 'SPOT',
    # High Growth Tech
    'PLTR', 'SNOW', 'CRWD', 'DKNG', 'COIN', 'RBLX', 'U', 'MNDY', 'NET', 'DDOG',
    'ZS', 'PANW', 'NOW', 'WDAY', 'TEAM', 'ZM', 'DOCU', 'FTNT', 'OKTA', 'MDB',
    # Semiconductors
    'TSM', 'ASML', 'AMAT', 'LRCX', 'KLAC', 'MRVL', 'MCHP', 'ADI', 'NXPI', 'ON',
    # Biotech
    'MRNA', 'BIIB', 'ILMN', 'ALNY', 'INCY', 'SGEN', 'EXAS', 'NBIX', 'TECH', 'RARE',
    # Retail & E-commerce
    'AMZN', 'BABA', 'JD', 'MELI', 'SE', 'SHOP', 'EBAY', 'ETSY', 'W', 'CHWY',
    # Automotive
    'TSLA', 'F', 'GM', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'STLA', 'HMC',
    # Finance Tech
    'PYPL', 'SQ', 'AFRM', 'SOFI', 'NU', 'COIN', 'MSTR', 'HOOD', 'UPST', 'LC',
    # Real Estate
    'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'SPG', 'O', 'WELL', 'DLR', 'AVB',
    # Materials
    'LIN', 'APD', 'SHW', 'ECL', 'DD', 'NEM', 'FCX', 'VMC', 'MLM', 'NUE',
    # Utilities
    'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'ES', 'PEG',
    # Consumer Discretionary
    'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TJX', 'LOW', 'BKNG', 'MAR',
    # Aerospace & Defense
    'BA', 'RTX', 'LMT', 'GD', 'NOC', 'HWM', 'TDG', 'LHX', 'TXT', 'HII',
    # Healthcare Equipment
    'TMO', 'ABT', 'DHR', 'ISRG', 'BSX', 'SYK', 'EW', 'BDX', 'RMD', 'IDXX',
    # Entertainment & Media
    'DIS', 'NFLX', 'CMCSA', 'WBD', 'PARA', 'FOX', 'FOXA', 'LYV', 'MSG', 'MSGS',
    # Clean Energy
    'ENPH', 'SEDG', 'FSLR', 'RUN', 'NOVA', 'PLUG', 'BE', 'BLNK', 'CHPT', 'QS'
]

# Dynamic category definitions (calculated in real-time)
DYNAMIC_CATEGORIES = {
    "📈 Top Gainers Today": {
        "description": "Highest percentage gainers in the current session",
        "type": "dynamic",
        "filter": "top_gainers"
    },
    "📉 Top Losers Today": {
        "description": "Largest percentage decliners in the current session",
        "type": "dynamic",
        "filter": "top_losers"
    },
    "🔥 Most Active": {
        "description": "Highest volume compared to average (volume surge)",
        "type": "dynamic",
        "filter": "most_active"
    },
    "⚡ Breakout Stocks": {
        "description": "Price above 20-day SMA with volume surge",
        "type": "dynamic",
        "filter": "breakout"
    },
    "💎 Oversold Opportunities": {
        "description": "RSI below 30 - potentially undervalued",
        "type": "dynamic",
        "filter": "oversold"
    },
    "🚀 Momentum Leaders": {
        "description": "Strongest 5-day momentum with high volume",
        "type": "dynamic",
        "filter": "momentum"
    },
    "🏆 52-Week High Breakers": {
        "description": "Stocks near or at 52-week highs",
        "type": "dynamic",
        "filter": "high_breakers"
    },
    "🎯 Value Plays": {
        "description": "Low P/E ratio stocks with positive momentum",
        "type": "dynamic",
        "filter": "value"
    }
}

# Static curated categories (pre-selected tickers)
STATIC_CATEGORIES = {
    "💰 Blue Chips": {
        "description": "Large, stable, established companies",
        "type": "static",
        "tickers": ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'BRK-B', 'JPM', 'V', 'MA', 'JNJ', 'PG']
    },
    "🤖 AI & Tech Leaders": {
        "description": "Artificial Intelligence and Technology powerhouses",
        "type": "static",
        "tickers": ['NVDA', 'AMD', 'GOOGL', 'MSFT', 'META', 'AVGO', 'PLTR', 'SNOW', 'CRWD', 'NET']
    },
    "💵 Dividend Champions": {
        "description": "Reliable dividend-paying stocks",
        "type": "static",
        "tickers": ['JNJ', 'PG', 'KO', 'PEP', 'MCD', 'VZ', 'T', 'XOM', 'CVX', 'ABBV']
    },
    "🔋 Clean Energy": {
        "description": "Renewable energy and EV companies",
        "type": "static",
        "tickers": ['TSLA', 'ENPH', 'SEDG', 'FSLR', 'NEE', 'PLUG', 'RUN', 'NOVA', 'RIVN', 'LCID']
    },
    "🎮 Entertainment & Gaming": {
        "description": "Gaming, streaming, and entertainment",
        "type": "static",
        "tickers": ['NFLX', 'DIS', 'RBLX', 'EA', 'TTWO', 'DKNG', 'WBD', 'SPOT', 'LYV', 'PARA']
    },
    "🔐 Cybersecurity": {
        "description": "Cybersecurity and data protection leaders",
        "type": "static",
        "tickers": ['CRWD', 'PANW', 'ZS', 'FTNT', 'OKTA', 'NET', 'S', 'CHKP', 'CYBR', 'RPD']
    },
    "☁️ Cloud Computing": {
        "description": "Cloud infrastructure and SaaS",
        "type": "static",
        "tickers": ['MSFT', 'AMZN', 'GOOGL', 'SNOW', 'CRM', 'ORCL', 'NOW', 'DDOG', 'MDB', 'NET']
    },
    "💊 Healthcare Leaders": {
        "description": "Healthcare and biotech companies",
        "type": "static",
        "tickers": ['JNJ', 'UNH', 'LLY', 'ABBV', 'MRK', 'PFE', 'TMO', 'ABT', 'DHR', 'ISRG']
    }
}

# Function to calculate stock universe data
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def calculate_stock_universe():
    """Calculate metrics for entire stock universe"""
    stocks_data = []
    
    # Remove duplicates from universe
    unique_tickers = list(set(STOCK_UNIVERSE))
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(unique_tickers):
        try:
            status_text.text(f"Loading {ticker}... ({idx + 1}/{len(unique_tickers)})")
            stock = yf.Ticker(ticker)
            
            # Get historical data
            hist_5d = stock.history(period="5d")
            hist_20d = stock.history(period="1mo")
            hist_1y = stock.history(period="1y")
            
            if len(hist_5d) >= 2 and len(hist_20d) >= 5:
                info = stock.info
                
                # Current values
                current_price = hist_5d['Close'].iloc[-1]
                prev_close = hist_5d['Close'].iloc[0]
                
                # Calculate metrics
                change_pct = ((current_price - prev_close) / prev_close) * 100
                volume = hist_5d['Volume'].iloc[-1]
                avg_volume = hist_20d['Volume'].mean()
                volume_ratio = volume / avg_volume if avg_volume > 0 else 0
                
                # Calculate SMA
                sma_20 = hist_20d['Close'].rolling(window=20).mean().iloc[-1] if len(hist_20d) >= 20 else current_price
                above_sma = current_price > sma_20
                
                # Calculate RSI
                delta = hist_20d['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = (100 - (100 / (1 + rs))).iloc[-1] if len(gain) >= 14 else 50
                
                # 52-week high
                if len(hist_1y) > 0:
                    week_52_high = hist_1y['High'].max()
                    pct_from_high = ((current_price - week_52_high) / week_52_high) * 100
                else:
                    week_52_high = current_price
                    pct_from_high = 0
                
                stocks_data.append({
                    'Ticker': ticker,
                    'Name': info.get('shortName', ticker)[:30],
                    'Price': current_price,
                    'Change %': change_pct,
                    'Volume': volume,
                    'Avg Volume': avg_volume,
                    'Volume Ratio': volume_ratio,
                    'Market Cap': info.get('marketCap', 0),
                    'Sector': info.get('sector', 'N/A'),
                    'PE Ratio': info.get('trailingPE', None),
                    'SMA 20': sma_20,
                    'Above SMA': above_sma,
                    'RSI': rsi,
                    '52W High': week_52_high,
                    '% From 52W High': pct_from_high
                })
                
            progress_bar.progress((idx + 1) / len(unique_tickers))
        except Exception as e:
            # Skip stocks that fail to load
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(stocks_data)

# Function to filter stocks by dynamic category
def filter_by_category(df, category_filter):
    """Filter stocks based on dynamic category criteria"""
    if category_filter == "top_gainers":
        return df.nlargest(20, 'Change %')
    
    elif category_filter == "top_losers":
        return df.nsmallest(20, 'Change %')
    
    elif category_filter == "most_active":
        # Highest volume relative to average
        return df.nlargest(20, 'Volume Ratio')
    
    elif category_filter == "breakout":
        # Above 20-day SMA with volume surge
        breakout = df[(df['Above SMA'] == True) & (df['Volume Ratio'] > 1.5)]
        return breakout.nlargest(20, 'Volume Ratio')
    
    elif category_filter == "oversold":
        # RSI below 30
        oversold = df[df['RSI'] < 30]
        return oversold.sort_values('RSI')
    
    elif category_filter == "momentum":
        # Positive change with high volume
        momentum = df[(df['Change %'] > 0) & (df['Volume Ratio'] > 1.2)]
        return momentum.nlargest(20, 'Change %')
    
    elif category_filter == "high_breakers":
        # Within 5% of 52-week high
        near_high = df[df['% From 52W High'] > -5]
        return near_high.sort_values('% From 52W High', ascending=False).head(20)
    
    elif category_filter == "value":
        # Low P/E with positive momentum
        value = df[(df['PE Ratio'].notna()) & (df['PE Ratio'] > 0) & (df['PE Ratio'] < 20) & (df['Change %'] > 0)]
        return value.sort_values('PE Ratio').head(20)
    
    return df

# Function to get stocks for static categories
@st.cache_data(ttl=1800)
def get_static_category_stocks(tickers):
    """Get data for a static list of tickers"""
    stocks_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(tickers):
        try:
            status_text.text(f"Loading {ticker}... ({idx + 1}/{len(tickers)})")
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            hist_20d = stock.history(period="1mo")
            info = stock.info
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[0]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                volume = hist['Volume'].iloc[-1]
                avg_volume = hist_20d['Volume'].mean()
                
                # Calculate RSI
                delta = hist_20d['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = (100 - (100 / (1 + rs))).iloc[-1] if len(gain) >= 14 else 50
                
                stocks_data.append({
                    'Ticker': ticker,
                    'Name': info.get('shortName', ticker)[:30],
                    'Price': current_price,
                    'Change %': change_pct,
                    'Volume': volume,
                    'Avg Volume': avg_volume,
                    'Volume Ratio': volume / avg_volume if avg_volume > 0 else 0,
                    'Market Cap': info.get('marketCap', 0),
                    'Sector': info.get('sector', 'N/A'),
                    'PE Ratio': info.get('trailingPE', None),
                    'RSI': rsi
                })
            progress_bar.progress((idx + 1) / len(tickers))
        except:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(stocks_data)

# Function to calculate SMA
def calculate_sma(data, period):
    """Calculate Simple Moving Average"""
    return data['Close'].rolling(window=period).mean()

# Function to calculate RSI
def calculate_rsi(data, period=14):
    """Calculate Relative Strength Index"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate MACD
def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

# Function to interpret indicators
def get_simple_insights(current_price, sma_short_val, sma_long_val, rsi_val, macd_val, signal_val):
    """Generate beginner-friendly insights"""
    insights = []
    
    # Price trend analysis
    if current_price > sma_short_val > sma_long_val:
        insights.append("🟢 **Strong Uptrend**: Price is above both moving averages, suggesting strong upward momentum.")
    elif current_price > sma_short_val:
        insights.append("🟡 **Moderate Uptrend**: Price is above the short-term average but watch the longer trend.")
    elif current_price < sma_short_val < sma_long_val:
        insights.append("🔴 **Downtrend**: Price is below both averages, indicating potential weakness.")
    else:
        insights.append("🟡 **Mixed Signals**: The trend is unclear. Wait for clearer direction.")
    
    # RSI analysis
    if rsi_val > 70:
        insights.append(f"⚠️ **Overbought (RSI: {rsi_val:.1f})**: Stock may be expensive. Consider waiting for a dip.")
    elif rsi_val < 30:
        insights.append(f"💡 **Oversold (RSI: {rsi_val:.1f})**: Stock may be undervalued. Could be a buying opportunity.")
    else:
        insights.append(f"✅ **Neutral RSI ({rsi_val:.1f})**: Price is in a healthy range.")
    
    # MACD analysis
    if macd_val > signal_val and macd_val > 0:
        insights.append("📈 **MACD Bullish**: Momentum is positive and strengthening. Good sign for buyers.")
    elif macd_val < signal_val and macd_val < 0:
        insights.append("📉 **MACD Bearish**: Momentum is negative. Consider caution.")
    else:
        insights.append("➡️ **MACD Neutral**: Momentum is unclear. No strong signal.")
    
    return insights

# ============= DISCOVER STOCKS PAGE =============
if page == "🔍 Discover Stocks":
    st.header("🔥 Discover Stocks by Category")
    st.markdown("Explore curated lists of stocks across different categories and market segments")
    
    # Category selection
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_category = st.selectbox(
            "Choose a category:",
            options=list(STOCK_CATEGORIES.keys()),
            format_func=lambda x: x
        )
    with col2:
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    # Display category description
    st.info(f"**{selected_category}**: {STOCK_CATEGORIES[selected_category]['description']}")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        min_change = st.slider("Min Price Change %", -20.0, 20.0, -10.0, 1.0)
    with col2:
        sector_filter = st.selectbox("Sector", ["All", "Technology", "Healthcare", "Financial Services", 
                                                  "Consumer Cyclical", "Communication Services", "Industrials",
                                                  "Energy", "Real Estate", "Consumer Defensive"])
    with col3:
        sort_by = st.selectbox("Sort By", ["Change %", "Volume", "Market Cap", "Price"])
    
    with st.spinner(f"Loading {selected_category}..."):
        df_stocks = get_stocks_by_category(selected_category)
    
    if not df_stocks.empty:
        # Apply filters
        df_filtered = df_stocks[df_stocks['Change %'] >= min_change].copy()
        
        if sector_filter != "All":
            df_filtered = df_filtered[df_filtered['Sector'] == sector_filter]
        
        # Sort
        ascending = False if sort_by == "Change %" else False
        df_filtered = df_filtered.sort_values(by=sort_by, ascending=ascending)
        
        # Display summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_change = df_filtered['Change %'].mean()
            st.metric("Avg Change", f"{avg_change:+.2f}%")
        with col2:
            top_gainer = df_filtered.nlargest(1, 'Change %')
            if not top_gainer.empty:
                st.metric("Top Gainer", top_gainer.iloc[0]['Ticker'], 
                         f"{top_gainer.iloc[0]['Change %']:+.2f}%")
        with col3:
            st.metric("Stocks Found", len(df_filtered))
        with col4:
            total_volume = df_filtered['Volume'].sum()
            st.metric("Total Volume", f"{total_volume/1e9:.2f}B")
        
        st.markdown("---")
        
        # Display stocks in cards
        st.subheader(f"📋 {selected_category} Stocks")
        
        # Format the dataframe for display
        df_display = df_filtered.copy()
        df_display['Price'] = df_display['Price'].apply(lambda x: f"${x:.2f}")
        df_display['Change %'] = df_display['Change %'].apply(lambda x: f"{x:+.2f}%")
        df_display['Volume'] = df_display['Volume'].apply(lambda x: f"{x/1e6:.1f}M")
        df_display['Market Cap'] = df_display['Market Cap'].apply(
            lambda x: f"${x/1e9:.1f}B" if x > 0 else "N/A"
        )
        
        # Add PE Ratio if available
        if 'PE Ratio' in df_display.columns:
            df_display['PE Ratio'] = df_display['PE Ratio'].apply(
                lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
            )
        
        # Display as interactive table
        st.dataframe(
            df_display[['Ticker', 'Name', 'Price', 'Change %', 'Volume', 'Market Cap', 'Sector', 'PE Ratio']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Name": st.column_config.TextColumn("Company", width="medium"),
                "Price": st.column_config.TextColumn("Price", width="small"),
                "Change %": st.column_config.TextColumn("5-Day Change", width="small"),
                "Volume": st.column_config.TextColumn("Volume", width="small"),
                "Market Cap": st.column_config.TextColumn("Market Cap", width="small"),
                "Sector": st.column_config.TextColumn("Sector", width="medium"),
                "PE Ratio": st.column_config.TextColumn("P/E", width="small"),
            }
        )
        
        # Quick analyze section
        st.markdown("---")
        st.subheader("🎯 Quick Analyze")
        selected_ticker = st.selectbox(
            "Select a stock to analyze:",
            options=df_filtered['Ticker'].tolist(),
            format_func=lambda x: f"{x} - {df_filtered[df_filtered['Ticker']==x]['Name'].iloc[0]}"
        )
        
        if st.button("📊 Analyze This Stock", type="primary"):
            st.session_state['selected_ticker'] = selected_ticker
            st.rerun()
    else:
        st.warning("Unable to load stock data. Please try again later.")
    
    # Stock screener section
    with st.expander("🔍 Custom Stock Screener"):
        st.markdown("""
        ### Add Your Own Tickers
        Enter stock symbols separated by commas to create a custom watchlist.
        """)
        custom_tickers = st.text_input("Enter tickers (e.g., PLTR, SOFI, RIVN):")
        if custom_tickers and st.button("Load Custom List"):
            custom_list = [t.strip().upper() for t in custom_tickers.split(',')]
            st.session_state['custom_tickers'] = custom_list
            st.success(f"Loading {len(custom_list)} custom tickers...")
            st.rerun()
        
        # Show custom list if exists
        if 'custom_tickers' in st.session_state:
            st.markdown("#### Your Custom List:")
            st.write(", ".join(st.session_state['custom_tickers']))
            if st.button("Clear Custom List"):
                del st.session_state['custom_tickers']
                st.rerun()
    
    # Quick category navigation
    st.markdown("---")
    st.subheader("🚀 Quick Category Navigation")
    st.markdown("*Click on any category to explore:*")
    
    cols = st.columns(4)
    popular_categories = ["🔥 Trending Now", "📈 Top Gainers", "🤖 AI & Tech", "💰 Blue Chips", 
                         "💎 High Growth", "⚡ Momentum", "💵 Dividend Payers", "🔋 Clean Energy"]
    
    for idx, cat in enumerate(popular_categories):
        with cols[idx % 4]:
            if st.button(cat, key=f"quick_{cat}", use_container_width=True):
                st.session_state['selected_category'] = cat
                st.rerun()

# ============= ANALYZE STOCK PAGE =============
else:
    st.header("📊 Stock Technical Analysis")
    
    # Check if ticker was selected from discovery page
    if 'selected_ticker' in st.session_state:
        default_ticker = st.session_state['selected_ticker']
        del st.session_state['selected_ticker']
    else:
        default_ticker = "AAPL"
    
    # Analysis parameters
    st.sidebar.subheader("Analysis Parameters")
    ticker = st.sidebar.text_input("Stock Ticker Symbol", value=default_ticker).upper()
    
    period_options = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y"
    }
    period_label = st.sidebar.selectbox("Time Period", list(period_options.keys()), index=3)
    period = period_options[period_label]
    
    # Technical indicator parameters
    st.sidebar.subheader("Technical Indicators")
    sma_short = st.sidebar.slider("Short SMA Period", 5, 50, 20)
    sma_long = st.sidebar.slider("Long SMA Period", 50, 200, 50)
    rsi_period = st.sidebar.slider("RSI Period", 5, 30, 14)
    
    # Load data
    try:
        with st.spinner(f"Loading data for {ticker}..."):
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                st.error(f"No data found for ticker '{ticker}'. Please check the symbol and try again.")
                st.stop()
            
            # Get company info
            info = stock.info
            company_name = info.get('longName', ticker)
            
            # Calculate technical indicators
            df['SMA_Short'] = calculate_sma(df, sma_short)
            df['SMA_Long'] = calculate_sma(df, sma_long)
            df['RSI'] = calculate_rsi(df, rsi_period)
            df['MACD'], df['Signal'], df['Histogram'] = calculate_macd(df)
            
            # Remove NaN values for cleaner display
            df_clean = df.dropna()
            
            # Current values
            current_price = df_clean['Close'].iloc[-1]
            prev_close = df_clean['Close'].iloc[-2]
            price_change = current_price - prev_close
            price_change_pct = (price_change / prev_close) * 100
            
            current_rsi = df_clean['RSI'].iloc[-1]
            current_macd = df_clean['MACD'].iloc[-1]
            current_signal = df_clean['Signal'].iloc[-1]
            current_sma_short = df_clean['SMA_Short'].iloc[-1]
            current_sma_long = df_clean['SMA_Long'].iloc[-1]
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()
    
    # Display company info and key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=f"{company_name}",
            value=f"${current_price:.2f}",
            delta=f"{price_change_pct:+.2f}%"
        )
    
    with col2:
        st.metric(
            label="Volume",
            value=f"{df_clean['Volume'].iloc[-1]:,.0f}"
        )
    
    with col3:
        st.metric(
            label=f"{sma_short}-Day SMA",
            value=f"${current_sma_short:.2f}"
        )
    
    with col4:
        st.metric(
            label="RSI",
            value=f"{current_rsi:.1f}"
        )
    
    # Generate insights
    st.subheader("📊 Simple Insights (What This Means)")
    insights = get_simple_insights(
        current_price, current_sma_short, current_sma_long,
        current_rsi, current_macd, current_signal
    )
    
    for insight in insights:
        st.markdown(insight)
    
    st.markdown("---")
    
    # Create interactive charts
    st.subheader("📈 Interactive Charts")
    
    # Chart 1: Price and Moving Averages
    fig1 = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price & Moving Averages', 'Volume')
    )
    
    # Candlestick chart
    fig1.add_trace(
        go.Candlestick(
            x=df_clean.index,
            open=df_clean['Open'],
            high=df_clean['High'],
            low=df_clean['Low'],
            close=df_clean['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Moving averages
    fig1.add_trace(
        go.Scatter(
            x=df_clean.index,
            y=df_clean['SMA_Short'],
            mode='lines',
            name=f'SMA {sma_short}',
            line=dict(color='orange', width=2)
        ),
        row=1, col=1
    )
    
    fig1.add_trace(
        go.Scatter(
            x=df_clean.index,
            y=df_clean['SMA_Long'],
            mode='lines',
            name=f'SMA {sma_long}',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    # Volume
    fig1.add_trace(
        go.Bar(
            x=df_clean.index,
            y=df_clean['Volume'],
            name='Volume',
            marker_color='lightblue'
        ),
        row=2, col=1
    )
    
    fig1.update_layout(
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Chart 2: RSI
    fig2 = go.Figure()
    
    fig2.add_trace(
        go.Scatter(
            x=df_clean.index,
            y=df_clean['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='purple', width=2)
        )
    )
    
    # Add overbought/oversold lines
    fig2.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
    fig2.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
    fig2.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral (50)")
    
    fig2.update_layout(
        title='Relative Strength Index (RSI)',
        height=300,
        yaxis_title='RSI',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Chart 3: MACD
    fig3 = make_subplots(
        rows=1, cols=1,
        subplot_titles=('MACD Indicator',)
    )
    
    fig3.add_trace(
        go.Scatter(
            x=df_clean.index,
            y=df_clean['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue', width=2)
        )
    )
    
    fig3.add_trace(
        go.Scatter(
            x=df_clean.index,
            y=df_clean['Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='orange', width=2)
        )
    )
    
    # Histogram
    colors = ['green' if val >= 0 else 'red' for val in df_clean['Histogram']]
    fig3.add_trace(
        go.Bar(
            x=df_clean.index,
            y=df_clean['Histogram'],
            name='Histogram',
            marker_color=colors
        )
    )
    
    fig3.update_layout(
        height=300,
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Explanation section
    with st.expander("📚 What Do These Indicators Mean?"):
        st.markdown("""
        ### Simple Moving Average (SMA)
        - **What it is**: The average price over a specific number of days.
        - **How to use it**: 
            - When price is **above** the SMA → Upward trend (bullish)
            - When price is **below** the SMA → Downward trend (bearish)
            - When short SMA crosses above long SMA → Buy signal
            - When short SMA crosses below long SMA → Sell signal
        
        ### Relative Strength Index (RSI)
        - **What it is**: Measures if a stock is overbought or oversold (0-100 scale).
        - **How to use it**:
            - RSI > 70 → **Overbought** (might drop soon)
            - RSI < 30 → **Oversold** (might rise soon)
            - RSI around 50 → Neutral
        
        ### MACD (Moving Average Convergence Divergence)
        - **What it is**: Shows the relationship between two moving averages.
        - **How to use it**:
            - MACD above Signal line → **Bullish** momentum
            - MACD below Signal line → **Bearish** momentum
            - Histogram growing → Momentum strengthening
            - Histogram shrinking → Momentum weakening
        
        **Remember**: No single indicator is perfect! Always use multiple indicators together and consider other factors before making investment decisions.
        """)

# Footer
st.markdown("---")
st.caption(f"Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data source: Yahoo Finance")
st.caption("⚠️ Disclaimer: This is for educational purposes only. Not financial advice. Always do your own research before investing.")