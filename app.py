import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# ==================== PAGE ====================
st.set_page_config(page_title="Forex Auto Trader", layout="wide")
st.title("🚀 Forex Automated Trading Bot")

# ==================== SETTINGS ====================
st.sidebar.header("Settings")

selected_pair = st.sidebar.selectbox(
    "Select Asset",
    ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "USDCHF=X", "BTC-USD", "GC=F"]
)

# ==================== DATA FETCH ====================
@st.cache_data(ttl=10)
def get_real_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="5m", progress=False)

        if df.empty:
            return pd.DataFrame()

        # 🔥 FIX 1: Flatten MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        # 🔥 FIX 2: Normalize timestamp
        if "Datetime" in df.columns:
            df.rename(columns={"Datetime": "timestamp"}, inplace=True)
        elif "Date" in df.columns:
            df.rename(columns={"Date": "timestamp"}, inplace=True)

        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # 🔥 FIX 3: Rename safely
        df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)

        # 🔥 FIX 4: Keep ONLY valid columns that exist
        valid_cols = ["timestamp", "open", "high", "low", "close", "volume"]
        df = df[[col for col in valid_cols if col in df.columns]]

        # 🔥 FIX 5: Add volume if missing (forex case)
        if "volume" not in df.columns:
            df["volume"] = 0

        return df

    except Exception as e:
        st.error(f"Data error: {e}")
        return pd.DataFrame()

# ==================== LOAD ====================
df_5m = get_real_data(selected_pair)

if df_5m.empty:
    st.warning("No data")
    st.stop()

# ==================== DEBUG (IMPORTANT) ====================
st.write("Columns received:", df_5m.columns.tolist())

# ==================== PREP ====================
df_5m = df_5m.sort_values("timestamp")
df_5m = df_5m.set_index("timestamp")

# ==================== SAFE RESAMPLE ====================
def safe_resample(df, rule):
    needed = ["open", "high", "low", "close", "volume"]

    # 🔥 Only use columns that actually exist
    existing = [col for col in needed if col in df.columns]

    if len(existing) < 4:
        st.error(f"Not enough valid columns for {rule}")
        return pd.DataFrame()

    agg_map = {}
    if "open" in existing: agg_map["open"] = "first"
    if "high" in existing: agg_map["high"] = "max"
    if "low" in existing: agg_map["low"] = "min"
    if "close" in existing: agg_map["close"] = "last"
    if "volume" in existing: agg_map["volume"] = "sum"

    try:
        return df.resample(rule).agg(agg_map).dropna().reset_index()
    except Exception as e:
        st.error(f"Resample failed: {e}")
        return pd.DataFrame()

# ==================== RESAMPLING ====================
df_15m = safe_resample(df_5m, "15min")
df_1h = safe_resample(df_5m, "1h")
df_daily = safe_resample(df_5m, "1D")

# ==================== CHECK ====================
if df_daily.empty:
    st.warning("⚠️ Not enough higher timeframe data")
    st.stop()

# ==================== DAILY BIAS ====================
df_daily["ema9"] = df_daily["close"].ewm(span=9).mean()
df_daily["ema21"] = df_daily["close"].ewm(span=21).mean()

bias = "BULLISH" if df_daily["ema9"].iloc[-1] > df_daily["ema21"].iloc[-1] else "BEARISH"

st.info(f"Bias: {bias}")

# ==================== CHART ====================
st.subheader("5M Chart")
st.line_chart(df_5m["close"])

# ==================== 15M ====================
if not df_15m.empty:
    st.subheader("15M Chart")
    st.line_chart(df_15m.set_index("timestamp")["close"])

# ==================== 1H ====================
if not df_1h.empty:
    st.subheader("1H Chart")
    st.line_chart(df_1h.set_index("timestamp")["close"])

# ==================== DAILY ====================
st.subheader("Daily Chart")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_daily["timestamp"], y=df_daily["close"], name="Price"))
fig.add_trace(go.Scatter(x=df_daily["timestamp"], y=df_daily["ema9"], name="EMA 9"))
fig.add_trace(go.Scatter(x=df_daily["timestamp"], y=df_daily["ema21"], name="EMA 21"))

st.plotly_chart(fig, use_container_width=True)

st.success("App running successfully ✅")
