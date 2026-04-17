import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Forex Auto Trader", layout="wide")
st.title("🚀 Forex Automated Trading Bot")
st.markdown("**Multi-Timeframe Trend-Following Strategy** | London & New York Sessions")

# ==================== TEST MODE ====================
st.sidebar.header("Settings")
test_mode = st.sidebar.checkbox("Test Mode (Dummy Data)", value=True)

# ==================== DUMMY DATA FUNCTION (Fixed) ====================
def get_dummy_data():
    dates = pd.date_range(end=datetime.now(), periods=300, freq='5min')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': 1.0850 + pd.Series(range(300)) * 0.00008,
        'high': 1.0850 + pd.Series(range(300)) * 0.00008 + 0.0006,
        'low': 1.0850 + pd.Series(range(300)) * 0.00008 - 0.0006,
        'close': 1.0850 + pd.Series(range(300)) * 0.00008 + 0.0003,
        'volume': 1200 + pd.Series(range(300)) * 15
    })
    
    # Fixed resampling with lowercase 'h' instead of 'H'
    return {
        '1d': df.resample('D', on='timestamp').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).reset_index(),
        
        '1h': df.resample('h', on='timestamp').agg({      # Changed 'H' → 'h'
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).reset_index(),
        
        '15m': df.resample('15min', on='timestamp').agg({
            'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
        }).reset_index(),
        
        '5m': df
    }

# Load dummy data
data = get_dummy_data()

# Daily bias calculation
df_daily = data['1d'].copy()
df_daily['ema9'] = df_daily['close'].ewm(span=9).mean()
df_daily['ema21'] = df_daily['close'].ewm(span=21).mean()
daily_bias = "BULLISH" if df_daily['ema9'].iloc[-1] > df_daily['ema21'].iloc[-1] else "BEARISH"

st.info(f"**Daily Bias:** {daily_bias} | Current Session: London / New York")

# Multi-timeframe tabs
tabs = st.tabs(["Daily", "1H", "15M", "5M"])

with tabs[0]:
    st.write("Daily Bias Determination")
    st.line_chart(df_daily.set_index('timestamp')[['close', 'ema9', 'ema21']])

with tabs[1]:
    st.write("1H Structure & Supply/Demand Zones (Coming soon)")
    st.line_chart(data['1h'].set_index('timestamp')['close'])

with tabs[2]:
    st.write("15M EMA(9/21) + RSI Confirmation (Coming soon)")
    st.line_chart(data['15m'].set_index('timestamp')['close'])

with tabs[3]:
    st.write("5M Entry Trigger (Coming soon)")
    st.line_chart(data['5m'].set_index('timestamp')['close'])

# Trading Controls
st.subheader("Trading Controls")
col1, col2 = st.columns(2)
with col1:
    if st.button("Start Live Trading", type="primary"):
        st.success("✅ Bot started in LIVE mode")
with col2:
    if st.button("Start Paper Trading"):
        st.info("📋 Paper trading mode activated")

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

st.caption("Built with Streamlit • Strategy logic in progress")
