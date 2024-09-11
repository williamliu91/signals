import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Function to calculate William's %R
def williams_r(df, period=14):
    highest_high = df['High'].rolling(window=period).max()
    lowest_low = df['Low'].rolling(window=period).min()
    wr = (highest_high - df['Close']) / (highest_high - lowest_low) * -100
    return wr

# Function to calculate support and resistance levels based on most price touches
def identify_support_resistance_levels(df, period):
    support_levels = []
    resistance_levels = []

    for i in range(period, len(df) - period):
        low_period = df['Low'].iloc[i - period:i + period + 1].min()
        high_period = df['High'].iloc[i - period:i + period + 1].max()

        if df['Low'].iloc[i] == low_period:
            support_levels.append(df['Low'].iloc[i])

        if df['High'].iloc[i] == high_period:
            resistance_levels.append(df['High'].iloc[i])

    lowest_support = min(support_levels) if support_levels else None
    highest_resistance = max(resistance_levels) if resistance_levels else None

    if support_levels:
        most_support = max(set(support_levels), key=support_levels.count)
    else:
        most_support = None

    if resistance_levels:
        most_resistance = max(set(resistance_levels), key=resistance_levels.count)
    else:
        most_resistance = None

    return lowest_support, most_support, highest_resistance, most_resistance

# Function to generate buy/sell signals based on Williams %R and Support/Resistance levels
def generate_trading_signals(df, most_support, most_resistance):
    buy_signals = []
    sell_signals = []

    for i in range(1, len(df)):
        # Buy Signal: Williams %R crosses above -80 and price touches support
        if df['Williams %R'].iloc[i - 1] < -80 and df['Williams %R'].iloc[i] > -80 and df['Low'].iloc[i] <= most_support:
            buy_signals.append((df.index[i], df['Close'].iloc[i]))

        # Sell Signal: Williams %R crosses below -20 and price touches resistance
        if df['Williams %R'].iloc[i - 1] > -20 and df['Williams %R'].iloc[i] < -20 and df['High'].iloc[i] >= most_resistance:
            sell_signals.append((df.index[i], df['Close'].iloc[i]))

    return buy_signals, sell_signals

# Fetch stock data and calculate indicators
def get_stock_data(symbol, period='1y'):
    stock_data = yf.download(symbol, period=period)
    stock_data['Williams %R'] = williams_r(stock_data)
    
    lowest_support, most_support, highest_resistance, most_resistance = identify_support_resistance_levels(stock_data, period=14)
    
    buy_signals, sell_signals = generate_trading_signals(stock_data, most_support, most_resistance)
    
    return stock_data.dropna(), lowest_support, most_support, highest_resistance, most_resistance, buy_signals, sell_signals

# Function to plot the stock data and support/resistance levels along with trading signals
def plot_stock_data(df, lowest_support, most_support, highest_resistance, most_resistance, buy_signals, sell_signals):
    # Create a subplot with two rows: one for price chart and one for William's %R
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, subplot_titles=('Stock Price with Key Support and Resistance', 'Williams %R'),
                        row_heights=[0.7, 0.3])

    # Add Candlestick chart for stock price
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['Open'], high=df['High'],
                                 low=df['Low'], close=df['Close'],
                                 name='Price'), row=1, col=1)

    # Add key Support and Resistance levels as horizontal lines
    if most_support:
        fig.add_trace(go.Scatter(x=df.index, y=[most_support] * len(df), mode='lines', 
                                 name=f'Support (Most Touches) {most_support:.2f}', 
                                 line=dict(color='green', width=2, dash='dash')), row=1, col=1)

    if most_resistance:
        fig.add_trace(go.Scatter(x=df.index, y=[most_resistance] * len(df), mode='lines', 
                                 name=f'Resistance (Most Touches) {most_resistance:.2f}', 
                                 line=dict(color='red', width=2, dash='dash')), row=1, col=1)

    # Add Buy signals
    if buy_signals:
        buy_dates, buy_prices = zip(*buy_signals)
        fig.add_trace(go.Scatter(x=buy_dates, y=buy_prices, mode='markers', 
                                 marker=dict(color='blue', size=15, symbol='triangle-up'),
                                 name='Buy Signal'), row=1, col=1)

    # Add Sell signals
    if sell_signals:
        sell_dates, sell_prices = zip(*sell_signals)
        fig.add_trace(go.Scatter(x=sell_dates, y=sell_prices, mode='markers', 
                                 marker=dict(color='blue', size=15, symbol='triangle-down'),
                                 name='Sell Signal'), row=1, col=1)

    # Add Williams %R indicator
    fig.add_trace(go.Scatter(x=df.index, y=df['Williams %R'], mode='lines', 
                             name="Williams %R", line=dict(color='blue', width=2)), row=2, col=1)

    # Add overbought/oversold reference lines for Williams %R
    fig.add_trace(go.Scatter(x=df.index, y=[-20]*len(df), mode='lines', name='Overbought',
                             line=dict(color='purple', dash='dash')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=[-80]*len(df), mode='lines', name='Oversold',
                             line=dict(color='purple', dash='dash')), row=2, col=1)

    # Update layout
    fig.update_layout(height=800, width=1000, title_text="Stock Analysis with Support/Resistance, Williams %R, and Trading Signals",
                      xaxis_rangeslider_visible=False)

    # Return the figure
    return fig

# Streamlit App
st.title('Stock Chart with Trading Signals, Support & Resistance, and Williams %R')

# Dropdown for stock selection
symbol = st.selectbox('Select Stock', ['GOOGL', 'AAPL', 'META', 'MSFT'])

# Dropdown for time period selection
period = st.selectbox('Select Time Period', ['1mo', '3mo', '6mo', '1y'], index=3)

# Fetch data and plot the chart based on selected stock and period
df, lowest_support, most_support, highest_resistance, most_resistance, buy_signals, sell_signals = get_stock_data(symbol, period)
fig = plot_stock_data(df, lowest_support, most_support, highest_resistance, most_resistance, buy_signals, sell_signals)
st.plotly_chart(fig)
