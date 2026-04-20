import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Forex Auto Trader", layout="wide")
st.title("🚀 Forex Automated Trading Bot")
st.markdown("**Multi-Timeframe Trend-Following Strategy** | London & New York Sessions")

# ==================== TEST MODE ====================
st.sidebar.header("Settings")
st.sidebar.info("✅ Running in Test Mode with Realistic Data")

# ==================== REALISTIC DUMMY DATA ====================
def get_realistic_dummy_data():
    # Generate more realistic price series
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=800, freq='5min')
    
    # Base price with trend and noise
    base_price = 1.0850
    trend = np.linspace(0, 0.015, 800)  # Slight upward trend
    noise = np.random.normal(0, 0.0008, 800)
    prices = base_price + trend + np.cumsum(noise)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': prices + np.random.uniform(0.0004, 0.0012, 800),
        'low': prices - np.random.uniform(0.0004, 0.0012, 800),
        'close': prices + np.random.normal(0, 0.0003, 800),
        'volume': np.random.randint(800, 2500, 800)
    })
    
    # Resample to different timeframes
    return {
        '1d': df.resample('D', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index(),
        '1h': df.resample('h', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index(),
        '15m': df.resample('15min', on='timestamp').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'}).reset_index(),
        '5m': df
    }

data = get_realistic_dummy_data()

# ==================== STRATEGY LOGIC ====================
def calculate_strategy_signals(data):
    signals = {}
    
    # Daily Bias
    df_d = data['1d'].copy()
    df_d['ema9'] = df_d['close'].ewm(span=9).mean()
    df_d['ema21'] = df_d['close'].ewm(span=21).mean()
    daily_bias = "BULLISH" if df_d['ema9'].iloc[-1] > df_d['ema21'].iloc[-1] else "BEARISH"
    signals['daily_bias'] = daily_bias
    
    # 15M Confirmation
    df_15 = data['15m'].copy()
    df_15['ema9'] = df_15['close'].ewm(span=9).mean()
    df_15['ema21'] = df_15['close'].ewm(span=21).mean()
    df_15['rsi'] = pd.Series(50 + 25 * np.sin(np.arange(len(df_15))/10))  # Simulated RSI
    ema_aligned = df_15['ema9'].iloc[-1] > df_15['ema21'].iloc[-1]
    rsi_ok = df_15['rsi'].iloc[-1] > 50
    signals['15m_confirmation'] = "BULLISH" if ema_aligned and rsi_ok else "BEARISH"
    
    # 5M Entry Trigger (simple price action)
    df_5 = data['5m'].copy()
    latest_candle = df_5.iloc[-1]
    prev_candle = df_5.iloc[-2]
    bullish_trigger = latest_candle['close'] > latest_candle['open'] and latest_candle['close'] > prev_candle['high']
    signals['5m_trigger'] = "LONG" if bullish_trigger else "SHORT"
    
    return signals

signals = calculate_strategy_signals(data)

# ==================== DASHBOARD ====================
st.info(f"**Daily Bias:** {signals['daily_bias']} | 15M Confirmation: {signals['15m_confirmation']} | 5M Trigger: {signals['5m_trigger']}")

tabs = st.tabs(["Daily", "1H", "15M", "5M"])

with tabs[0]:
    st.write("Daily Bias Determination")
    df_d = data['1d']
    df_d['ema9'] = df_d['close'].ewm(span=9).mean()
    df_d['ema21'] = df_d['close'].ewm(span=21).mean()
    st.line_chart(df_d.set_index('timestamp')[['close', 'ema9', 'ema21']])

with tabs[1]:
    st.write("1H Structure (Supply/Demand Zones - Simulated)")
    st.line_chart(data['1h'].set_index('timestamp')['close'])

with tabs[2]:
    st.write("15M EMA(9/21) + RSI Confirmation")
    df_15 = data['15m']
    df_15['ema9'] = df_15['close'].ewm(span=9).mean()
    df_15['ema21'] = df_15['close'].ewm(span=21).mean()
    st.line_chart(df_15.set_index('timestamp')[['close', 'ema9', 'ema21']])

with tabs[3]:
    st.write("5M Entry Trigger")
    st.line_chart(data['5m'].set_index('timestamp')['close'])

# Trading Controls
st.subheader("Trading Controls")
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Live Trading", type="primary"):
        st.success("✅ Strategy signals generated - Bot would trade now (Demo)")
with col2:
    if st.button("Start Paper Trading"):
        st.info("📋 Paper trading simulation active")

# Info Section
st.markdown("---")
st.subheader("INFO")
st.markdown("""
This project is given by S.I.R at workshop17 Cape Town and develop by Charles Oni (+27814272490).We welcome contributions, donations, and feedback from users, and supporters. 
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
