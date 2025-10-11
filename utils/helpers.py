"""
Utility helper functions for the application.
"""

import streamlit as st
from typing import Dict, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def display_api_status():
    """Display API connection status in sidebar"""
    from config.settings import config
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔌 API Status")
    
    keys = config.validate_keys()
    
    if keys['gemini']:
        st.sidebar.success("✅ Gemini AI Connected")
    else:
        st.sidebar.warning("⚠️ Gemini AI Not Connected")
        st.sidebar.caption("Set GEMINI_API_KEY to enable AI analysis")
    
    if keys['fmp']:
        st.sidebar.success("✅ FMP Data Connected")
    else:
        st.sidebar.warning("⚠️ FMP Not Connected")
        st.sidebar.caption("Set FMP_API_KEY for fundamentals")


def format_large_number(num: float) -> str:
    """Format large numbers with K/M/B suffix"""
    if num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    elif num >= 1e3:
        return f"${num/1e3:.2f}K"
    else:
        return f"${num:.2f}"


def create_price_chart(df: pd.DataFrame, 
                       sma_short: pd.Series, 
                       sma_long: pd.Series,
                       title: str = "Price & Moving Averages") -> go.Figure:
    """
    Create interactive price chart with volume
    
    Args:
        df: DataFrame with OHLCV data
        sma_short: Short SMA series
        sma_long: Long SMA series
        title: Chart title
    
    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(title, 'Volume')
    )
    
    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # SMAs
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=sma_short,
            mode='lines',
            name=f'SMA {len(sma_short)}',
            line=dict(color='orange', width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=sma_long,
            mode='lines',
            name=f'SMA {len(sma_long)}',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    # Volume
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color='lightblue'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig


def create_rsi_chart(df: pd.DataFrame, rsi: pd.Series) -> go.Figure:
    """Create RSI chart with overbought/oversold lines"""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=rsi,
            mode='lines',
            name='RSI',
            line=dict(color='purple', width=2)
        )
    )
    
    # Reference lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
    fig.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral (50)")
    
    fig.update_layout(
        title='Relative Strength Index (RSI)',
        height=300,
        yaxis_title='RSI',
        hovermode='x unified'
    )
    
    return fig


def create_macd_chart(df: pd.DataFrame, 
                     macd: pd.Series, 
                     signal: pd.Series, 
                     histogram: pd.Series) -> go.Figure:
    """Create MACD chart with histogram"""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=macd,
            mode='lines',
            name='MACD',
            line=dict(color='blue', width=2)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=signal,
            mode='lines',
            name='Signal',
            line=dict(color='orange', width=2)
        )
    )
    
    # Histogram
    colors = ['green' if val >= 0 else 'red' for val in histogram]
    fig.add_trace(
        go.Bar(
            x=df.index,
            y=histogram,
            name='Histogram',
            marker_color=colors
        )
    )
    
    fig.update_layout(
        title='MACD Indicator',
        height=300,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig


def display_recommendation_card(analysis: Dict):
    """
    Display AI recommendation in a nice card format
    
    Args:
        analysis: Gemini analysis results
    """
    if not analysis:
        st.warning("AI analysis not available. Check API keys.")
        return
    
    recommendation = analysis.get('recommendation', 'HOLD')
    confidence = analysis.get('confidence', 5)
    reasoning = analysis.get('reasoning', 'No reasoning provided')
    
    # Color based on recommendation
    if recommendation == 'BUY':
        color = 'green'
        emoji = '🟢'
    elif recommendation == 'SELL':
        color = 'red'
        emoji = '🔴'
    else:
        color = 'orange'
        emoji = '🟡'
    
    st.markdown(f"""
    <div style="padding: 20px; border-radius: 10px; border: 2px solid {color}; background-color: rgba(0,0,0,0.1);">
        <h2 style="color: {color};">{emoji} {recommendation}</h2>
        <p style="font-size: 18px;"><strong>Confidence:</strong> {confidence}/10</p>
        <p style="font-size: 16px;">{reasoning}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Entry and exit points
    col1, col2, col3 = st.columns(3)
    
    entry = analysis.get('entry_point', {})
    stop_loss = analysis.get('stop_loss', {})
    target = analysis.get('target_price', {})
    
    with col1:
        if entry.get('price'):
            st.metric("📍 Entry Point", f"${entry['price']:.2f}")
            st.caption(entry.get('rationale', ''))
    
    with col2:
        if stop_loss.get('price'):
            st.metric("🛑 Stop Loss", f"${stop_loss['price']:.2f}")
            st.caption(stop_loss.get('rationale', ''))
    
    with col3:
        if target.get('price_3month'):
            upside = target.get('upside_potential', 0)
            st.metric("🎯 3M Target", f"${target['price_3month']:.2f}", 
                     f"{upside:+.1f}%" if upside else None)
            st.caption(target.get('rationale', ''))
    
    # Risk factors and catalysts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚠️ Risk Factors")
        risks = analysis.get('risk_factors', [])
        for risk in risks:
            st.markdown(f"- {risk}")
    
    with col2:
        st.markdown("### 🚀 Catalysts")
        catalysts = analysis.get('catalysts', [])
        for catalyst in catalysts:
            st.markdown(f"- {catalyst}")


def get_signal_color(signal: str) -> str:
    """Get color for signal display"""
    if 'BUY' in signal.upper():
        return 'green'
    elif 'SELL' in signal.upper():
        return 'red'
    else:
        return 'gray'


def get_signal_emoji(signal: str) -> str:
    """Get emoji for signal"""
    if 'STRONG BUY' in signal.upper():
        return '🟢🟢'
    elif 'BUY' in signal.upper():
        return '🟢'
    elif 'STRONG SELL' in signal.upper():
        return '🔴🔴'
    elif 'SELL' in signal.upper():
        return '🔴'
    else:
        return '🟡'