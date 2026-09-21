import ccxt
import pandas as pd
import plotly.graph_objects as go
import gradio as gr
import spaces  # 1. นำเข้าไลบรารี spaces ของ Hugging Face


# 2. ใส่ Decorator นี้ไว้เหนือฟังก์ชันที่ต้องการให้รันบน ZeroGPU
@spaces.GPU
def get_market_data(symbol, timeframe):
  try:
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    df = pd.DataFrame(
        ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    # คำนวณ Moving Average 20
    df['MA20'] = df['close'].rolling(window=20).mean()

    # สร้างกราฟ Candlestick ด้วย Plotly
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['MA20'],
            name='MA 20',
            line=dict(color='orange'),
        )
    )

    fig.update_layout(
        title=f'{symbol} - Timeframe {timeframe}',
        xaxis_title='Time',
        yaxis_title='Price (USDT)',
        template='plotly_dark',
    )

    latest_price = f'ราคาล่าสุด ({symbol}): {df["close"].iloc[-1]:,.2f} USDT'
    return fig, latest_price
  except Exception as e:
    return None, f'เกิดข้อผิดพลาดในการดึงข้อมูล: {e}'


# สร้างหน้าตาเว็บแอปด้วย Gradio Blocks
with gr.Blocks() as demo:
  gr.Markdown('# 📈 AI & Crypto Trading Analysis Dashboard')
  gr.Markdown('เลือกคู่เหรียญและช่วงเวลาที่ต้องการวิเคราะห์ข้อมูลตลาดแบบเรียลไทม์')

  with gr.Row():
    symbol_input = gr.Dropdown(
        choices=['BTC/USDT', 'ETH/USDT', 'SOL/USDT'],
        value='BTC/USDT',
        label='Trading Pair',
    )
    timeframe_input = gr.Dropdown(
        choices=['1h', '4h', '1d'], value='1h', label='Timeframe'
    )

  btn = gr.Button('โหลดข้อมูล / วิเคราะห์กราฟ', variant='primary')

  price_output = gr.Textbox(label='สรุปราคาปัจจุบัน')
  plot_output = gr.Plot(label='กราฟราคาทางเทคนิค')

  btn.click(
      fn=get_market_data,
      inputs=[symbol_input, timeframe_input],
      outputs=[plot_output, price_output],
  )

if __name__ == '__main__':
  demo.launch(theme=gr.themes.Soft())
    
