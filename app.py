import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# ==================== PAGE ====================
st.set_page_config(page_title="Forex Auto Trader", layout="wide")
st.title("🚀 Forex Automated Trading Bot")
st.markdown("**Multi-Timeframe Trend-Following Strategy** | Live Data from Yahoo Finance")

# ==================== SETTINGS ====================
st.sidebar.header("Settings")

selected_pair = st.sidebar.selectbox(
    "Select Asset",
    ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "USDCHF=X", "BTC-USD", "GC=F"]
)

update_interval = st.sidebar.slider(
    "Chart Update Interval (seconds)", 3, 15, 5
)

st.sidebar.info("✅ Using real live data from Yahoo Finance")

# ==================== DATA FETCH ====================
@st.cache_data(ttl=5)
def get_real_data(symbol):
    try:
        data = yf.download(
            symbol,
            period="5d",
            interval="5m",
            progress=False
        )

        if data.empty:
            return pd.DataFrame()

        data = data.reset_index()

        # Handle both possible column names
        if "Datetime" in data.columns:
            data.rename(columns={"Datetime": "timestamp"}, inplace=True)
        elif "Date" in data.columns:
            data.rename(columns={"Date": "timestamp"}, inplace=True)

        # 🔥 CRITICAL FIX
        data["timestamp"] = pd.to_datetime(data["timestamp"])

        data.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)

        return data

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# ==================== LOAD DATA ====================
df_5m = get_real_data(selected_pair)

if df_5m.empty:
    st.warning("⚠️ No data received. Try another asset or refresh.")
    st.stop()

# ==================== RESAMPLING ====================
df_5m = df_5m.set_index("timestamp")

df_15m = df_5m.resample("15min").agg({
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum"
}).dropna().reset_index()

df_1h = df_5m.resample("1h").agg({
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum"
}).dropna().reset_index()

df_daily = df_5m.resample("1D").agg({
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "volume": "sum"
}).dropna().reset_index()

# ==================== DAILY BIAS ====================
df_daily["ema9"] = df_daily["close"].ewm(span=9).mean()
df_daily["ema21"] = df_daily["close"].ewm(span=21).mean()

daily_bias = "BULLISH" if df_daily["ema9"].iloc[-1] > df_daily["ema21"].iloc[-1] else "BEARISH"

st.info(
    f"**Daily Bias:** {daily_bias} | Pair: {selected_pair} | Last Updated: {datetime.now().strftime('%H:%M:%S')}"
)

# ==================== TABS ====================
tabs = st.tabs(["Daily", "1H", "15M", "5M"])

# -------- DAILY --------
with tabs[0]:
    st.subheader("Daily Bias (EMA 9 vs EMA 21)")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_daily["timestamp"],
        y=df_daily["close"],
        name="Price",
        line=dict(color="blue")
    ))
    fig.add_trace(go.Scatter(
        x=df_daily["timestamp"],
        y=df_daily["ema9"],
        name="EMA 9",
        line=dict(color="orange")
    ))
    fig.add_trace(go.Scatter(
        x=df_daily["timestamp"],
        y=df_daily["ema21"],
        name="EMA 21",
        line=dict(color="green")
    ))

    st.plotly_chart(fig, use_container_width=True)

# -------- 1H --------
with tabs[1]:
    st.subheader("1H Structure")
    st.line_chart(df_1h.set_index("timestamp")["close"])

# -------- 15M --------
with tabs[2]:
    st.subheader("15M EMA Strategy")

    df_15 = df_15m.copy()
    df_15["ema9"] = df_15["close"].ewm(span=9).mean()
    df_15["ema21"] = df_15["close"].ewm(span=21).mean()

    fig15 = go.Figure()
    fig15.add_trace(go.Scatter(
        x=df_15["timestamp"],
        y=df_15["close"],
        name="Price",
        line=dict(color="blue")
    ))
    fig15.add_trace(go.Scatter(
        x=df_15["timestamp"],
        y=df_15["ema9"],
        name="EMA 9",
        line=dict(color="orange")
    ))
    fig15.add_trace(go.Scatter(
        x=df_15["timestamp"],
        y=df_15["ema21"],
        name="EMA 21",
        line=dict(color="green")
    ))

    st.plotly_chart(fig15, use_container_width=True)

# -------- 5M --------
with tabs[3]:
    st.subheader("5M Entry Chart")
    st.line_chart(df_5m["close"])

# ==================== CONTROLS ====================
st.subheader("Trading Controls")

col1, col2 = st.columns(2)

with col1:
    if st.button("Start Live Trading", type="primary"):
        st.success("✅ Live strategy running (data only, no real trades yet)")

with col2:
    if st.button("Start Paper Trading"):
        st.info("📋 Paper trading mode activated")

# ==================== AUTO REFRESH ====================
st.caption(
    f"Refresh every {update_interval}s | Last update: {datetime.now().strftime('%H:%M:%S')}"
)

# ==================== FOOTER ====================
st.markdown("---")
st.subheader("INFO")

st.markdown("This app uses Yahoo Finance live market data.")

st.markdown("""
**Contact:**
- Email: onitechs@gmail.com

**Profiles:**
- LinkedIn: Charles Oni
- GitHub: mainbtpty
""")
