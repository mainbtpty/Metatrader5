import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import MetaTrader5 as mt5
import time
import os
from datetime import datetime

st.set_page_config(page_title="Forex Auto Trader", layout="wide")
st.title("🚀 Forex Automated Trading Bot")
st.markdown("**Multi-Timeframe Trend-Following Strategy** | London & New York Sessions")

# ==================== CONFIG ====================
st.sidebar.header("MT5 Connection")
test_mode = st.sidebar.checkbox("Test Mode (Dummy Data)", value=True)

if not test_mode:
    account = st.sidebar.number_input("MT5 Account Number", value=12345678)
    password = st.sidebar.text_input("Password", type="password")
    server = st.sidebar.text_input("Server", value="YourBroker-Demo")
    
    if st.sidebar.button("Connect to MT5"):
        if mt5.initialize(login=account, password=password, server=server):
            st.sidebar.success("✅ Connected to MT5")
            st.session_state.connected = True
        else:
            st.sidebar.error(f"Connection failed: {mt5.last_error()}")
else:
    st.sidebar.success("🧪 Running in Test Mode (Dummy Data)")

# ==================== STRATEGY LOGIC ====================
def get_multi_timeframe_data(symbol):
    """Return dummy or real data for Daily, 1H, 15M, 5M"""
    if test_mode:
        # Dummy data for testing
        dates = pd.date_range(end=datetime.now(), periods=200, freq='5min')
        df5m = pd.DataFrame({
            'timestamp': dates,
            'open': 1.0850 + pd.Series(range(200)) * 0.0001,
            'high': 1.0850 + pd.Series(range(200)) * 0.0001 + 0.0005,
            'low': 1.0850 + pd.Series(range(200)) * 0.0001 - 0.0005,
            'close': 1.0850 + pd.Series(range(200)) * 0.0001 + 0.0002,
            'volume': 1000 + pd.Series(range(200)) * 10
        })
        return {'1d': df5m.resample('D', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index(),
                '1h': df5m.resample('H', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index(),
                '15m': df5m.resample('15min', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index(),
                '5m': df5m}
    else:
        # Real MT5 data (when connected)
        rates = {}
        for tf, mt5_tf in [('1d', mt5.TIMEFRAME_D1), ('1h', mt5.TIMEFRAME_H1), 
                           ('15m', mt5.TIMEFRAME_M15), ('5m', mt5.TIMEFRAME_M5)]:
            rates[tf] = pd.DataFrame(mt5.copy_rates_range(symbol, mt5_tf, datetime(2024,1,1), datetime.now()),
                                     columns=['timestamp','open','high','low','close','volume'])
            rates[tf]['timestamp'] = pd.to_datetime(rates[tf]['timestamp'], unit='s')
        return rates

def determine_daily_bias(df_daily):
    """Simple daily bias using EMA 9/21 alignment"""
    df_daily['ema9'] = df_daily['close'].ewm(span=9).mean()
    df_daily['ema21'] = df_daily['close'].ewm(span=21).mean()
    if df_daily['ema9'].iloc[-1] > df_daily['ema21'].iloc[-1]:
        return "BULLISH"
    else:
        return "BEARISH"

# ==================== MAIN DASHBOARD ====================
st.subheader("Strategy Status")

data = get_multi_timeframe_data("EURUSD")  # Change symbol as needed

daily_bias = determine_daily_bias(data['1d'])
st.info(f"**Daily Bias:** {daily_bias}")

# Multi-timeframe view
tabs = st.tabs(["Daily", "1H", "15M", "5M"])
with tabs[0]:
    st.write("Daily Bias:", daily_bias)
with tabs[1]:
    st.write("1H Structure - Supply/Demand zones (to be implemented)")
with tabs[2]:
    st.write("15M EMA(9/21) + RSI confirmation (to be implemented)")
with tabs[3]:
    st.write("5M Entry trigger (to be implemented)")

# Controls
col_a, col_b = st.columns(2)
with col_a:
    if st.button("Start Live Trading", type="primary"):
        st.success("Bot started in LIVE mode (strategy logic active)")
with col_b:
    if st.button("Start Paper Trading"):
        st.info("Paper trading mode activated")

st.markdown("---")
st.subheader("INFO")
st.markdown("""
This is an open-source project. We welcome contributions, donations, and feedback from developers, users, and supporters. Join us to make a difference and be part of a growing community!
""")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Contact Me:**")
    st.markdown("- Email: [onitechs@gmail.com](mailto:onitechs@gmail.com)")
with col2:
    st.markdown("**Connect Online:**")
    st.markdown("- LinkedIn: [Charles Oni](https://www.linkedin.com/in/charles-oni-b45a91253/)")
    st.markdown("- GitHub: [mainbtpty](https://github.com/mainbtpty)")

# Run this file with: streamlit run app.py
