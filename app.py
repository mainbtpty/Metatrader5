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
risk_percent = st.sidebar.slider("Risk per Trade (%)", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

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

base_prices = {
    "EURUSD": 1.0850, "USDJPY": 152.50, "GBPUSD": 1.3050,
    "USDCHF": 0.8650, "BTCUSD": 68500, "XAUUSD (GOLD)": 2650
}

df_5m = generate_simulated_data(base_prices.get(selected_pair, 1.0850))

# Resample
df_15m = df_5m.resample('15min', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()
df_1h = df_5m.resample('h', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()
df_daily = df_5m.resample('D', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()

# ==================== FULL STRATEGY LOGIC ====================
# Daily Bias
df_daily['ema9'] = df_daily['close'].ewm(span=9).mean()
df_daily['ema21'] = df_daily['close'].ewm(span=21).mean()
daily_bias = "BULLISH" if df_daily['ema9'].iloc[-1] > df_daily['ema21'].iloc[-1] else "BEARISH"

# 15M EMA + RSI Confirmation
df_15 = df_15m.copy()
df_15['ema9'] = df_15['close'].ewm(span=9).mean()
df_15['ema21'] = df_15['close'].ewm(span=21).mean()
delta = df_15['close'].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
rs = gain / loss
df_15['rsi'] = 100 - (100 / (1 + rs))
rsi_value = df_15['rsi'].iloc[-1]
rsi_confirmation = "BULLISH" if rsi_value > 50 else "BEARISH"
ema_aligned = df_15['ema9'].iloc[-1] > df_15['ema21'].iloc[-1]
confirmation_15m = "BULLISH" if ema_aligned and rsi_confirmation == "BULLISH" else "BEARISH"

# 5M Price Action Trigger
df_5 = df_5m.copy()
latest = df_5.iloc[-1]
prev = df_5.iloc[-2]
bullish_trigger = (latest['close'] > latest['open']) and (latest['close'] > prev['high'])
bearish_trigger = (latest['close'] < latest['open']) and (latest['close'] < prev['low'])
entry_signal = "LONG" if bullish_trigger else "SHORT" if bearish_trigger else "NO SIGNAL"

# Overall Signal
overall_signal = "LONG" if daily_bias == "BULLISH" and confirmation_15m == "BULLISH" and entry_signal == "LONG" else \
                 "SHORT" if daily_bias == "BEARISH" and confirmation_15m == "BEARISH" and entry_signal == "SHORT" else "NO SIGNAL"

st.info(f"**Daily Bias:** {daily_bias} | 15M Confirmation: {confirmation_15m} (RSI: {rsi_value:.1f}) | 5M Trigger: {entry_signal} | **Overall Signal: {overall_signal}**")

# ==================== CHARTS ====================
tabs = st.tabs(["Daily", "1H", "15M", "5M"])

with tabs[0]:
    st.write("Daily Bias Determination")
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
    st.metric("15M RSI", f"{rsi_value:.1f}", delta=rsi_confirmation)

with tabs[3]:
    st.write("5M Entry Trigger")
    st.line_chart(df_5m.set_index('timestamp')['close'])

# Risk Management Display
st.subheader("Risk Management")
risk_amount = 10000 * (risk_percent / 100)  # Assuming $10,000 balance for demo
st.metric("Risk per Trade", f"{risk_percent}% (${risk_amount:.2f})")
st.metric("Max Daily Loss", "3%")
st.metric("Max Open Trades", "3")

# Trading Controls
st.subheader("Trading Controls")
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Live Trading", type="primary"):
        st.success(f"✅ Strategy Signal: {overall_signal} | Risk: {risk_percent}%")
with col2:
    if st.button("Start Paper Trading"):
        st.info("📋 Paper trading simulation active")

# Auto-refresh
time.sleep(update_interval)
st.rerun()

# ==================== INFO SECTION ====================
st.markdown("---")
st.subheader("INFO")
st.markdown("""
This is an on going project, and you are very welcome to donate and contribute your awesome comments, questions, or resources!

**Contact Me:**

- Email: [onitechs@gmail.com](mailto:onitechs@gmail.com)

**Connect Online:**

- LinkedIn: [Charles Oni](https://www.linkedin.com/in/charles-oni-b45a91253/)

- GitHub: [mainbtpty](https://github.com/mainbtpty)
""")
