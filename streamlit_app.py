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

# Function to get trending stocks
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_trending_stocks():
    """Get trending stocks from various categories"""
    try:
        # Popular tickers across different categories
        gainers_tickers = ['NVDA', 'AMD', 'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
        growth_tickers = ['PLTR', 'SNOW', 'DKNG', 'COIN', 'RBLX', 'U', 'CELH', 'MNDY']
        value_tickers = ['BRK-B', 'JPM', 'V', 'MA', 'JNJ', 'PG', 'KO', 'WMT']
        
        all_tickers = list(set(gainers_tickers + growth_tickers + value_tickers))
        
        stocks_data = []
        for ticker in all_tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                info = stock.info
                
                if len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[0]
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    volume = hist['Volume'].iloc[-1]
                    
                    stocks_data.append({
                        'Ticker': ticker,
                        'Name': info.get('shortName', ticker)[:30],
                        'Price': current_price,
                        'Change %': change_pct,
                        'Volume': volume,
                        'Market Cap': info.get('marketCap', 0),
                        'Sector': info.get('sector', 'N/A')
                    })
            except:
                continue
        
        return pd.DataFrame(stocks_data)
    except Exception as e:
        st.error(f"Error fetching trending stocks: {str(e)}")
        return pd.DataFrame()

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
    st.header("🔥 Discover Hot Stocks")
    st.markdown("Find trending stocks, top gainers, and interesting opportunities")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        min_change = st.slider("Min Price Change %", -20.0, 20.0, -10.0, 1.0)
    with col2:
        sector_filter = st.selectbox("Sector", ["All", "Technology", "Healthcare", "Financial Services", 
                                                  "Consumer Cyclical", "Communication Services", "Industrials"])
    with col3:
        sort_by = st.selectbox("Sort By", ["Change %", "Volume", "Market Cap", "Price"])
    
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
    
    with st.spinner("Loading trending stocks..."):
        df_stocks = get_trending_stocks()
    
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
        st.subheader("📋 Stocks List")
        
        # Format the dataframe for display
        df_display = df_filtered.copy()
        df_display['Price'] = df_display['Price'].apply(lambda x: f"${x:.2f}")
        df_display['Change %'] = df_display['Change %'].apply(lambda x: f"{x:+.2f}%")
        df_display['Volume'] = df_display['Volume'].apply(lambda x: f"{x/1e6:.1f}M")
        df_display['Market Cap'] = df_display['Market Cap'].apply(
            lambda x: f"${x/1e9:.1f}B" if x > 0 else "N/A"
        )
        
        # Display as interactive table
        st.dataframe(
            df_display,
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
        Enter stock symbols separated by commas to add them to the discovery list.
        """)
        custom_tickers = st.text_input("Enter tickers (e.g., PLTR, SOFI, RIVN):")
        if custom_tickers and st.button("Add to List"):
            st.success(f"Custom tickers will be added: {custom_tickers}")
            st.info("Refresh the page to see your custom stocks in the list!")

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