# Save this code in a file named `app.py`

import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np  # Import numpy

def get_nasdaq_data():
    data = yf.download('^IXIC', start='2024-01-01', end='2024-09-07')
    return data

def calculate_ema(data, period):
    return data['Close'].ewm(span=period, adjust=False).mean()

def generate_signals(data, ema1_period, ema2_period):
    data['EMA1'] = calculate_ema(data, ema1_period)
    data['EMA2'] = calculate_ema(data, ema2_period)
    
    # Generate signals
    data['Signal'] = 0
    data['Signal'] = np.where(data['EMA1'] > data['EMA2'], 1, 0)
    data['Position'] = data['Signal'].diff()
    
    # Buy and Sell signals
    buy_signals = data[data['Position'] == 1]
    sell_signals = data[data['Position'] == -1]
    
    return buy_signals, sell_signals

def plot_ema_chart(data, ema1_period, ema2_period):
    buy_signals, sell_signals = generate_signals(data, ema1_period, ema2_period)
    
    fig = go.Figure()
    
    # Candlestick Chart
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'],
                                 name='Candlestick'))
    
    # EMA Lines
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA1'], mode='lines', name=f'EMA {ema1_period}', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=data.index, y=data['EMA2'], mode='lines', name=f'EMA {ema2_period}', line=dict(color='red')))
    
    # Buy and Sell Signals
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'], mode='markers', name='Buy Signal', marker=dict(color='green', symbol='triangle-up', size=10)))
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'], mode='markers', name='Sell Signal', marker=dict(color='red', symbol='triangle-down', size=10)))
    
    fig.update_layout(title='NASDAQ with EMAs and Trading Signals',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False)
    
    return fig

def main():
    st.title('NASDAQ Chart with EMAs and Trading Signals')
    
    # Fetch data
    data = get_nasdaq_data()
    
    # EMA Period Inputs
    ema1_period = st.slider('Select EMA1 Length:', min_value=1, max_value=200, value=12)
    ema2_period = st.slider('Select EMA2 Length:', min_value=1, max_value=200, value=26)
    
    # Generate and Plot Chart
    fig = plot_ema_chart(data, ema1_period, ema2_period)
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
