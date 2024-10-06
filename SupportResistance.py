import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# Title for the Streamlit app
st.title("Stock Price Analysis with Buy/Sell Signals")

# List of top 50 stocks
top_stocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'FB', 'BRK.B', 'NVDA', 'JPM', 'JNJ',
    'V', 'PG', 'UNH', 'HD', 'DIS',
    'MA', 'PYPL', 'VZ', 'NFLX', 'INTC',
    'CMCSA', 'T', 'PEP', 'KO', 'CSCO',
    'NKE', 'MRK', 'XOM', 'TMO', 'PFE',
    'ABT', 'AVGO', 'COST', 'CRM', 'MDT',
    'NVS', 'AMGN', 'LLY', 'HON', 'QCOM',
    'LMT', 'TXN', 'IBM', 'AMD', 'ADBE',
    'CVX', 'PM', 'TGT', 'SBUX', 'NOW'
]

# Dropdown for selecting stock ticker
ticker = st.sidebar.selectbox("Select Stock:", top_stocks)

# Dropdown for selecting time period
time_period = st.sidebar.selectbox(
    "Select Time Period:",
    ["5 Years", "3 Years", "1 Year", "6 Months", "3 Months", "1 Month"]
)

# Calculate the start date based on the selected time period
end_date = datetime.now()
if time_period == "5 Years":
    start_date = end_date - timedelta(days=5*365)
elif time_period == "3 Years":
    start_date = end_date - timedelta(days=3*365)
elif time_period == "1 Year":
    start_date = end_date - timedelta(days=365)
elif time_period == "6 Months":
    start_date = end_date - timedelta(days=6*30)
elif time_period == "3 Months":
    start_date = end_date - timedelta(days=3*30)
else:  # "1 Month"
    start_date = end_date - timedelta(days=30)

# Fetch historical data for the selected stock within the specified date range
data = yf.download(ticker, start=start_date, end=end_date)

# Resetting index for proper date handling
data.reset_index(inplace=True)

# Input for threshold percentage from the user
percentage = st.sidebar.slider("Threshold Percentage (%)", 1, 20, 2)

# Define support and resistance levels
most_support = data['Close'].min()  # Calculate actual most support
most_resistance = data['Close'].max()  # Calculate actual most resistance

# Function to add buy and sell signals
def add_signals(data, most_support, most_resistance, percentage):
    # Calculate thresholds
    buy_threshold_high = most_support * (1 + percentage / 100)  # Buy threshold above most support
    buy_threshold_low = most_support * (1 - percentage / 100)   # Buy threshold below most support
    sell_threshold_high = most_resistance * (1 + percentage / 100)  # Sell threshold above most resistance
    sell_threshold_low = most_resistance * (1 - percentage / 100)   # Sell threshold below most resistance

    # Buy when the closing price is within the defined range around the support
    buy_signal = (data['Close'] <= buy_threshold_high) & (data['Close'] >= buy_threshold_low)

    # Sell when the closing price is within the defined range around the resistance
    sell_signal = (data['Close'] >= sell_threshold_low) & (data['Close'] <= sell_threshold_high)

    data['Buy'] = buy_signal
    data['Sell'] = sell_signal
    return data

# Add buy/sell signals to the DataFrame
data = add_signals(data, most_support, most_resistance, percentage)

# Prepare for Plotly Chart
fig = go.Figure(data=[go.Candlestick(x=data['Date'],
                                       open=data['Open'],
                                       high=data['High'],
                                       low=data['Low'],
                                       close=data['Close'])])

# Add most support and resistance lines
fig.add_shape(type="line",
              x0=data['Date'].iloc[0], x1=data['Date'].iloc[-1],
              y0=most_support, y1=most_support,
              line=dict(color="blue", width=2, dash="dash"),
              name="Most Support")

fig.add_shape(type="line",
              x0=data['Date'].iloc[0], x1=data['Date'].iloc[-1],
              y0=most_resistance, y1=most_resistance,
              line=dict(color="orange", width=2, dash="dash"),
              name="Most Resistance")

# Initialize variables for profit calculation
total_investment = 0
total_profit = 0
shares_held = 0

# Add buy and sell signals to the plot
for i in range(len(data)):
    if data['Buy'].iloc[i]:
        shares_bought = 1000 / data['Close'].iloc[i]  # Calculate number of shares bought
        total_investment += 1000  # Add $1000 to total investment
        shares_held += shares_bought  # Update shares held
        fig.add_trace(go.Scatter(
            x=[data['Date'].iloc[i]],
            y=[data['Close'].iloc[i]],
            mode='markers',
            marker=dict(color='blue', size=10, symbol='triangle-up'),
            name='Buy Signal'
        ))
    if data['Sell'].iloc[i] and shares_held > 0:
        total_profit += (data['Close'].iloc[i] * shares_held) - total_investment  # Calculate profit
        shares_held = 0  # Reset shares held after selling
        fig.add_trace(go.Scatter(
            x=[data['Date'].iloc[i]],
            y=[data['Close'].iloc[i]],
            mode='markers',
            marker=dict(color='red', size=10, symbol='triangle-down'),
            name='Sell Signal'
        ))

# Show the figure in Streamlit
st.plotly_chart(fig)

# Calculate ROI
roi = (total_profit / total_investment) * 100 if total_investment > 0 else 0

# Display the results
st.write("Data with Buy/Sell Signals:")
st.dataframe(data[['Date', 'Close', 'Buy', 'Sell']])
st.write(f"Return on Investment (ROI): {roi:.2f}%")
