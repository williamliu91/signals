import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta

# Function to get the top 50 stocks (example list)
def get_top_stocks():
    stocks = {
        "Apple": "AAPL",
        "Microsoft": "MSFT",
        "Alphabet": "GOOGL",
        "Amazon": "AMZN",
        "Tesla": "TSLA",
        "Meta": "META",
        "Berkshire Hathaway": "BRK-B",
        "Johnson & Johnson": "JNJ",
        "Visa": "V",
        "Walmart": "WMT",
        "Procter & Gamble": "PG",
        "UnitedHealth Group": "UNH",
        "NVIDIA": "NVDA",
        "Mastercard": "MA",
        "Coca-Cola": "KO",
        "Pfizer": "PFE",
        "PepsiCo": "PEP",
        "Intel": "INTC",
        "Cisco": "CSCO",
        "AbbVie": "ABBV",
        "Verizon": "VZ",
        "McDonald's": "MCD",
        "Nike": "NKE",
        "Salesforce": "CRM",
        "Exxon Mobil": "XOM",
        "Chevron": "CVX",
        "AT&T": "T",
        "Walt Disney": "DIS",
        "3M": "MMM",
        "IBM": "IBM",
        "Goldman Sachs": "GS",
        "American Express": "AXP",
        "Costco": "COST",
        "Honeywell": "HON",
        "Lowe's": "LOW",
        "Texas Instruments": "TXN",
        "Broadcom": "AVGO",
        "Qualcomm": "QCOM",
        "Starbucks": "SBUX",
        "Abbott Laboratories": "ABT",
        "Booking Holdings": "BKNG",
        "Danaher": "DHR",
        "PayPal": "PYPL",
        "Square": "SQ",
        "Applied Materials": "AMAT",
        "Lululemon": "LULU",
        "Caterpillar": "CAT",
        "Advanced Micro Devices": "AMD",
        "S&P Global": "SPGI"
    }
    return stocks

# Function to get start date based on selected period
def get_start_date(period):
    if period == "6 Month":
        return datetime.now() - timedelta(days=30 * 6)
    elif period == "3 Month":
        return datetime.now() - timedelta(days=30 * 3)
    elif period == "2 Month":
        return datetime.now() - timedelta(days=30 * 2)
    elif period == "1 Month":
        return datetime.now() - timedelta(days=30)

# Streamlit app
st.title("Stock Candlestick Chart")

# Select stock from the top 50
stocks = get_top_stocks()
selected_stock = st.selectbox("Select a stock:", list(stocks.keys()))

# Select time period
time_period = st.selectbox("Select time period:", 
                            ["6 Month", "3 Month", "2 Month", "1 Month"])

# Fetch stock data for the selected stock and time period
start_date = get_start_date(time_period)
ticker = stocks[selected_stock]
data = yf.download(ticker, start=start_date, end=datetime.now())

# Function to identify bullish after bearish candles and bearish engulfing signals
def identify_candle_patterns(df):
    # Identify bullish and bearish candles
    df['Bullish Candle'] = df['Close'] > df['Open']  # Current candle is bullish
    df['Bearish Candle'] = df['Close'] < df['Open']  # Current candle is bearish
    df['Prev Bullish'] = df['Close'].shift(1) > df['Open'].shift(1)  # Previous candle is bullish
    df['Prev Bearish'] = df['Close'].shift(1) < df['Open'].shift(1)  # Previous candle is bearish

    # Bearish engulfing conditions
    df['Prev Close < Curr Open'] = df['Close'].shift(1) < df['Open']  # Previous close < Current open
    df['Prev Open > Curr Close'] = df['Open'].shift(1) > df['Close']  # Previous open > Current close

    # Bullish after bearish conditions
    df['Bearish Close > Bullish Open'] = df['Close'].shift(1) > df['Open']  # Previous close > Current open
    df['Bearish Open < Bullish Close'] = df['Open'].shift(1) < df['Close']  # Previous open < Current close

    # Identify the bullish after bearish condition
    df['Bullish After Bearish'] = (df['Bullish Candle'] & 
                                   df['Prev Bearish'] & 
                                   df['Bearish Close > Bullish Open'] & 
                                   df['Bearish Open < Bullish Close'])
    
    # Identify the bearish engulfing condition
    df['Bearish Engulfing'] = (df['Bearish Candle'] & 
                               df['Prev Bullish'] & 
                               df['Prev Close < Curr Open'] & 
                               df['Prev Open > Curr Close'])
    
    return df

# Apply the function
data = identify_candle_patterns(data)

# Create a candlestick chart
fig = go.Figure(data=[go.Candlestick(x=data.index,
                                       open=data['Open'],
                                       high=data['High'],
                                       low=data['Low'],
                                       close=data['Close'],
                                       name='Candlestick')])

# Add markers for Bullish After Bearish Candles
fig.add_trace(go.Scatter(x=data.index[data['Bullish After Bearish']],
                         y=data['Low'][data['Bullish After Bearish']] - 2,
                         mode='markers',
                         marker=dict(symbol='triangle-up', size=10, color='green'),
                         name='Bullish After Bearish Candle'))

# Add markers for Bearish Engulfing Candles
fig.add_trace(go.Scatter(x=data.index[data['Bearish Engulfing']],
                         y=data['High'][data['Bearish Engulfing']] + 2,
                         mode='markers',
                         marker=dict(symbol='triangle-down', size=10, color='red'),
                         name='Bearish Engulfing Candle'))

# Customize layout
fig.update_layout(title=f'Bullish and Bearish Candle Patterns for {selected_stock}',
                  xaxis_title='Date',
                  yaxis_title='Price',
                  xaxis_rangeslider_visible=False)

# Show the chart in Streamlit
st.plotly_chart(fig)
