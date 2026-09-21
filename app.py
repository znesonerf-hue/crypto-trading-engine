import ccxt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="AI Trading & Market Analysis Dashboard", layout="wide"
)

st.title("📈 AI & Crypto Trading Analysis Dashboard")
st.sidebar.header("Configuration")

# เลือกเหรียญและตลาด
symbol = st.sidebar.selectbox(
    "Trading Pair", ["BTC/USDT", "ETH/USDT", "SOL/USDT"], index=0
)
timeframe = st.sidebar.selectbox(
    "Timeframe", ["1h", "4h", "1d"], index=0
)

@st.cache_data(ttl=300)
def fetch_data(symbol, timeframe):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    df = pd.DataFrame(
        ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

try:
    df = fetch_data(symbol, timeframe)
    
    # คำนวณ Moving Average เบื้องต้น (ตัวอย่าง AI/Indicator logic)
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    
    # แสดงกราฟราคาด้วย Plotly
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name='Market Price'
    ))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['MA20'], name='MA 20', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['MA50'], name='MA 50', line=dict(color='blue')))
    
    fig.update_layout(title=f"{symbol} Price Chart & AI Technical Indicators", xaxis_title="Time", yaxis_title="Price (USDT)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Market Summary")
    st.metric(label="Latest Close Price", value=f"{df['close'].iloc[-1]:,.2f} USDT")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
    
