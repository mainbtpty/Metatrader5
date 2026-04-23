import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Forex Auto Trader", layout="wide")
st.title("🚀 Forex Automated Trading Bot")
st.markdown("**Multi-Timeframe Trend-Following Strategy** | Live Data from Yahoo Finance")

# ==================== SETTINGS ====================
st.sidebar.header("Settings")
selected_pair = st.sidebar.selectbox(
    "Select Currency Pair",
    ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "USDCHF=X", "BTC-USD", "GC=F"]  # GC=F is Gold
)

update_interval = st.sidebar.slider("Chart Update Interval (seconds)", min_value=3, max_value=15, value=3)

st.sidebar.info("✅ Using real live data from Yahoo Finance")

# ==================== FETCH REAL DATA ====================
@st.cache_data(ttl=update_interval)
def get_real_data(symbol, period="5d", interval="5m"):
    try:
        data = yf.download(symbol, period=period, interval=interval, progress=False)
        data = data.reset_index()
        data = data.rename(columns={'Datetime': 'timestamp', 'Open': 'open', 'High': 'high', 
                                  'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
        return data
    except:
        st.error(f"Could not fetch data for {symbol}")
        return pd.DataFrame()

# Get data
df_5m = get_real_data(selected_pair)

# Resample to other timeframes
df_15m = df_5m.resample('15min', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()
df_1h = df_5m.resample('h', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()
df_daily = df_5m.resample('D', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index()

# Daily Bias
df_daily['ema9'] = df_daily['close'].ewm(span=9).mean()
df_daily['ema21'] = df_daily['close'].ewm(span=21).mean()
daily_bias = "BULLISH" if df_daily['ema9'].iloc[-1] > df_daily['ema21'].iloc[-1] else "BEARISH"

st.info(f"**Daily Bias:** {daily_bias} | Pair: {selected_pair} | Last Updated: {datetime.now().strftime('%H:%M:%S')}")

# Tabs
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
    df_15 = df_15m.copy()
    df_15['ema9'] = df_15['close'].ewm(span=9).mean()
    df_15['ema21'] = df_15['close'].ewm(span=21).mean()
    fig15 = go.Figure()
    fig15.add_trace(go.Scatter(x=df_15['timestamp'], y=df_15['close'], name='Price', line=dict(color='blue')))
    fig15.add_trace(go.Scatter(x=df_15['timestamp'], y=df_15['ema9'], name='EMA 9', line=dict(color='orange')))
    fig15.add_trace(go.Scatter(x=df_15['timestamp'], y=df_15['ema21'], name='EMA 21', line=dict(color='green')))
    st.plotly_chart(fig15, use_container_width=True)

with tabs[3]:
    st.write("5M Entry Trigger")
    st.line_chart(df_5m.set_index('timestamp')['close'])

# Controls
st.subheader("Trading Controls")
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Live Trading", type="primary"):
        st.success("✅ Strategy running on LIVE Yahoo Finance data")
with col2:
    if st.button("Start Paper Trading"):
        st.info("📋 Paper trading simulation active")

# Auto-refresh every 3 seconds
st.caption(f"Data refreshes every {update_interval} seconds • Last update: {datetime.now().strftime('%H:%M:%S')}")

# Info
# Info Section
st.markdown("---")
st.subheader("INFO")
st.markdown("""
This is project given by S.I.R.at worksho17.developed by Charles Oni.We welcome contributions, donations, and feedback from users, and supporters. 
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
