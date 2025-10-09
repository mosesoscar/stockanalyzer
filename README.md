# 📈 Stock Analysis Dashboard

A professional-grade, beginner-friendly stock analysis application built with Streamlit. Get real-time market data, technical indicators, and actionable insights—all translated into plain English.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 📊 Real-Time Data
- Live stock prices from Yahoo Finance
- Historical data from 1 month to 5 years
- Automatic updates and error handling

### 📉 Technical Indicators
- **SMA (Simple Moving Average)** - Trend identification with customizable periods
- **RSI (Relative Strength Index)** - Overbought/oversold detection
- **MACD** - Momentum analysis with signal lines and histogram

### 🎯 Beginner-Friendly Insights
- Automated plain-English explanations
- Color-coded signals (🟢 Bullish, 🔴 Bearish, 🟡 Neutral)
- Actionable recommendations for complete novices

### 📈 Interactive Visualizations
- Candlestick charts with volume
- RSI with overbought/oversold zones
- MACD with momentum histogram
- Hover tooltips for detailed data

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the repository**
```bash
git clone <your-repo-url>
cd stock-analysis-dashboard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run stock_analysis.py
```

4. **Open your browser**
The app will automatically open at `http://localhost:8501`

## 📖 How to Use

### Basic Usage
1. Enter a stock ticker symbol (e.g., `AAPL`, `TSLA`, `GOOGL`)
2. Select your preferred time period
3. View the automated insights and charts
4. Adjust technical indicator parameters in the sidebar

### Understanding the Dashboard

#### Top Metrics
- **Current Price** - Latest closing price with daily change
- **Volume** - Number of shares traded
- **SMA** - Moving average value
- **RSI** - Current momentum reading

#### Simple Insights Section
Get instant, plain-English interpretations:
- 🟢 **Strong signals** - Clear trends worth noting
- 🟡 **Neutral signals** - Wait for clearer direction
- 🔴 **Warning signals** - Proceed with caution

#### Charts
1. **Price & Volume** - See price trends and trading activity
2. **RSI Chart** - Identify overbought (>70) or oversold (<30) conditions
3. **MACD Chart** - Track momentum changes

### Customization
Adjust parameters in the sidebar:
- **Short SMA Period** (5-50 days) - Default: 20
- **Long SMA Period** (50-200 days) - Default: 50
- **RSI Period** (5-30 days) - Default: 14

## 📚 Technical Indicator Guide

### Simple Moving Average (SMA)
**What it does:** Smooths out price data to identify trends

**How to read it:**
- Price above SMA → Uptrend (bullish)
- Price below SMA → Downtrend (bearish)
- Short SMA crosses above long SMA → Buy signal
- Short SMA crosses below long SMA → Sell signal

### Relative Strength Index (RSI)
**What it does:** Measures momentum on a 0-100 scale

**How to read it:**
- RSI > 70 → Overbought (may drop)
- RSI < 30 → Oversold (may rise)
- RSI ≈ 50 → Neutral

### MACD (Moving Average Convergence Divergence)
**What it does:** Shows momentum and trend strength

**How to read it:**
- MACD above signal line → Bullish momentum
- MACD below signal line → Bearish momentum
- Growing histogram → Strengthening momentum
- Shrinking histogram → Weakening momentum

## 🛠️ Dependencies

- **streamlit** - Web application framework
- **yfinance** - Real-time financial data
- **pandas** - Data manipulation
- **numpy** - Numerical computations
- **plotly** - Interactive charts

## ⚠️ Important Disclaimers

1. **Not Financial Advice** - This tool is for educational purposes only
2. **Do Your Own Research** - Always verify information from multiple sources
3. **Past Performance ≠ Future Results** - Historical data doesn't guarantee future outcomes
4. **Risk Warning** - All investments carry risk; never invest more than you can afford to lose

## 🐛 Troubleshooting

### "No data found for ticker"
- Verify the ticker symbol is correct (use Yahoo Finance format)
- Check your internet connection
- Some international stocks may require exchange suffix (e.g., `BP.L` for London)

### Charts not loading
- Refresh the page (F5)
- Clear browser cache
- Ensure all dependencies are installed correctly

### Slow performance
- Try a shorter time period
- Close other browser tabs
- Check your internet speed

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Data provided by [Yahoo Finance](https://finance.yahoo.com/)
- Built with [Streamlit](https://streamlit.io/)
- Charts powered by [Plotly](https://plotly.com/)

## 📧 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the educational content in the app's expandable section
3. Submit an issue on GitHub

---

**Remember:** Successful investing requires patience, discipline, and continuous learning. Use this tool as one of many resources in your investment journey! 📚💡