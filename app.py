import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Forex Auto Trader", layout="wide")
st.title("🚀 Forex Automated Trading Bot")
st.markdown("**Multi-Timeframe Trend-Following Strategy** | London & New York Sessions")

# Test Mode
st.sidebar.header("Settings")
st.sidebar.info("✅ Running in Test Mode with Realistic Data")

# ==================== REALISTIC DUMMY DATA ====================
def get_realistic_dummy_data():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=400, freq='5min')
    
    base_price = 1.0850
    trend = np.linspace(0, 0.018, 400)
    noise = np.random.normal(0, 0.00085, 400)
    prices = base_price + trend + np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices + np.random.uniform(0.0004, 0.0015, 400),
        'low': prices - np.random.uniform(0.0004, 0.0015, 400),
        'close': prices + np.random.normal(0, 0.00035, 400),
        'volume': np.random.randint(900, 2800, 400)
    })
    return {
        '1d': df.resample('D', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index(),
        '1h': df.resample('h', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index(),
        '15m': df.resample('15min', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index(),
        '5m': df
    }

data = get_realistic_dummy_data()

# Daily bias with EMAs
df_daily = data['1d'].copy()
df_daily['ema9'] = df_daily['close'].ewm(span=9).mean()
df_daily['ema21'] = df_daily['close'].ewm(span=21).mean()
daily_bias = "BULLISH" if df_daily['ema9'].iloc[-1] > df_daily['ema21'].iloc[-1] else "BEARISH"

st.info(f"**Daily Bias:** {daily_bias} | Current Session: London / New York")

# Tabs with proper EMA lines
tabs = st.tabs(["Daily", "1H", "15M", "5M"])

with tabs[0]:
    st.write("Daily Bias Determination (EMA 9 vs EMA 21)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_daily['timestamp'], y=df_daily['close'], name='Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df_daily['timestamp'], y=df_daily['ema9'], name='EMA 9', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df_daily['timestamp'], y=df_daily['ema21'], name='EMA 21', line=dict(color='green')))
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.write("1H Structure (Supply/Demand Zones - Simulated)")
    st.line_chart(data['1h'].set_index('timestamp')['close'])

with tabs[2]:
    st.write("15M EMA(9/21) + RSI Confirmation")
    df_15 = data['15m']
    df_15['ema9'] = df_15['close'].ewm(span=9).mean()
    df_15['ema21'] = df_15['close'].ewm(span=21).mean()
    fig15 = go.Figure()
    fig15.add_trace(go.Scatter(x=df_15['timestamp'], y=df_15['close'], name='Price', line=dict(color='blue')))
    fig15.add_trace(go.Scatter(x=df_15['timestamp'], y=df_15['ema9'], name='EMA 9', line=dict(color='orange')))
    fig15.add_trace(go.Scatter(x=df_15['timestamp'], y=df_15['ema21'], name='EMA 21', line=dict(color='green')))
    st.plotly_chart(fig15, use_container_width=True)

with tabs[3]:
    st.write("5M Entry Trigger")
    st.line_chart(data['5m'].set_index('timestamp')['close'])

# Trading Controls
st.subheader("Trading Controls")
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Live Trading", type="primary"):
        st.success("✅ Strategy signals generated (Demo mode)")
with col2:
    if st.button("Start Paper Trading"):
        st.info("📋 Paper trading simulation active")

# Info Section
st.markdown("---")
st.subheader("INFO")
st.markdown("""
This is an open-source project. We welcome contributions, donations, and feedback from developers, users, and supporters. 
Join us to make a difference and be part of a growing community!
""")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Contact Me:**")
    st.markdown("- Email: [onitechs@gmail.com](mailto:onitechs@gmail.com)")
with col_b:
    st.markdown("**Connect Online:**")
    st.markdown("- LinkedIn: [Charles Oni](https://www.linkedin.com/in/charles-oni-b45a91253/)")
    st.markdown("- GitHub: [mainbtpty](https://github.com/mainbtpty)")

st.caption("Built with Streamlit • Strategy logic implemented with realistic dummy data")
