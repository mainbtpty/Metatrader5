import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import time

st.set_page_config(page_title="Forex Auto Trader", layout="wide")
st.title("🚀 Forex Automated Trading Bot")
st.markdown("**Multi-Timeframe Trend-Following Strategy** | Live Simulation")

# ==================== SETTINGS ====================
st.sidebar.header("Settings")
pairs = ["EURUSD", "USDJPY", "GBPUSD", "USDCHF", "BTCUSD", "XAUUSD (GOLD)"]
selected_pair = st.sidebar.selectbox("Select Pair", pairs)
update_interval = st.sidebar.slider("Auto Refresh Interval (seconds)", min_value=3, max_value=10, value=3)

st.sidebar.info("✅ Using realistic simulated live data (updates every " + str(update_interval) + " seconds)")

# ==================== REALISTIC SIMULATED DATA ====================
def generate_simulated_data(base_price=1.0850):
    np.random.seed(int(time.time()) % 100)
    dates = pd.date_range(end=datetime.now(), periods=400, freq='5min')
    
    trend = np.linspace(0, 0.00012 * 400, 400)
    noise = np.random.normal(0, 0.00095, 400)
    prices = base_price + trend + np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices + np.random.uniform(0.0005, 0.0018, 400),
        'low': prices - np.random.uniform(0.0005, 0.0018, 400),
        'close': prices + np.random.normal(0, 0.00045, 400),
        'volume': np.random.randint(950, 3200, 400)
    })
    return df

# Base prices for each pair
base_prices = {
    "EURUSD": 1.0850, "USDJPY": 152.50, "GBPUSD": 1.3050,
    "USDCHF": 0.8650, "BTCUSD": 68500, "XAUUSD (GOLD)": 2650
}

df_5m = generate_simulated_data(base_prices.get(selected_pair, 1.0850))

# Resample to other timeframes
df_15m = df_5m.resample('15min', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()
df_1h = df_5m.resample('h', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()
df_daily = df_5m.resample('D', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()

# ==================== STRATEGY LOGIC WITH RSI CONFIRMATION ====================
# Daily Bias
df_daily['ema9'] = df_daily['close'].ewm(span=9).mean()
df_daily['ema21'] = df_daily['close'].ewm(span=21).mean()
daily_bias = "BULLISH" if df_daily['ema9'].iloc[-1] > df_daily['ema21'].iloc[-1] else "BEARISH"

# 15M EMA + RSI Confirmation
df_15 = df_15m.copy()
df_15['ema9'] = df_15['close'].ewm(span=9).mean()
df_15['ema21'] = df_15['close'].ewm(span=21).mean()

# Simulated RSI (more realistic)
delta = df_15['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df_15['rsi'] = 100 - (100 / (1 + rs))

rsi_value = df_15['rsi'].iloc[-1]
rsi_confirmation = "BULLISH" if rsi_value > 50 else "BEARISH"
ema_aligned = df_15['ema9'].iloc[-1] > df_15['ema21'].iloc[-1]

final_confirmation = "BULLISH" if ema_aligned and rsi_confirmation == "BULLISH" else "BEARISH"

st.info(f"**Daily Bias:** {daily_bias} | 15M Confirmation (EMA + RSI): **{final_confirmation}** | RSI: {rsi_value:.1f}")

# ==================== CHARTS ====================
tabs = st.tabs(["Daily", "1H", "15M", "5M"])

with tabs[0]:
    st.write("Daily Bias Determination (EMA 9 vs EMA 21)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_daily['timestamp'], y=df_daily['close'], name='Price', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df_daily['timestamp'], y=df_daily['ema9'], name='EMA 9', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df_daily['timestamp'], y=df_daily['ema21'], name='EMA 21', line=dict(color='green')))
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.write("1H Structure")
    st.line_chart(df_1h.set_index('timestamp')['close'])

with tabs[2]:
    st.write("15M EMA(9/21) + RSI Confirmation")
    fig15 = go.Figure()
    fig15.add_trace(go.Scatter(x=df_15['timestamp'], y=df_15['close'], name='Price', line=dict(color='blue')))
    fig15.add_trace(go.Scatter(x=df_15['timestamp'], y=df_15['ema9'], name='EMA 9', line=dict(color='orange')))
    fig15.add_trace(go.Scatter(x=df_15['timestamp'], y=df_15['ema21'], name='EMA 21', line=dict(color='green')))
    st.plotly_chart(fig15, use_container_width=True)
    st.metric("15M RSI", f"{rsi_value:.1f}", delta="Bullish" if rsi_value > 50 else "Bearish")

with tabs[3]:
    st.write("5M Entry Trigger")
    st.line_chart(df_5m.set_index('timestamp')['close'])

# Auto-refresh
time.sleep(update_interval)
st.rerun()

# Trading Controls
st.subheader("Trading Controls")
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Live Trading", type="primary"):
        st.success("✅ Strategy running on simulated live data")
with col2:
    if st.button("Start Paper Trading"):
        st.info("📋 Paper trading simulation active")

# Info
st.markdown("---")
st.subheader("INFO")
st.markdown("""
This is an open-source project using realistic simulated market data. 
Real MetaTrader 5 connection will be added once we have a Windows VPS.
""")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Contact Me:**")
    st.markdown("- Email: [onitechs@gmail.com](mailto:onitechs@gmail.com)")
with col_b:
    st.markdown("**Connect Online:**")
    st.markdown("- LinkedIn: [Charles Oni](https://www.linkedin.com/in/charles-oni-b45a91253/)")
    st.markdown("- GitHub: [mainbtpty](https://github.com/mainbtpty)")
