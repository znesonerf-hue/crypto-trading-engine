import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import requests
import spaces


@spaces.GPU
def run_hybrid_trading_strategy(coin_id, vs_currency, short_window, long_window):
  try:
    # ดึงข้อมูลราคาย้อนหลัง 30 วันจาก CoinGecko API
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": "30"}
    response = requests.get(url, params=params)
    data = response.json()

    if "prices" not in data:
      return (
          None,
          f"ไม่สามารถดึงข้อมูลได้ (อาจติด Rate Limit): {data.get('status', 'Unknown error')}",
      )

    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # คำนวณ Moving Average (Hybrid Logic)
    df["SMA_Short"] = df["price"].rolling(window=int(short_window)).mean()
    df["SMA_Long"] = df["price"].rolling(window=int(long_window)).mean()

    # กำหนดสัญญาณซื้อ/ขาย (Signal Generation)
    df["Signal"] = 0
    df.loc[df["SMA_Short"] > df["SMA_Long"], "Signal"] = 1  # สัญญาณซื้อ (Buy)
    df.loc[df["SMA_Short"] <= df["SMA_Long"], "Signal"] = -1  # สัญญาณขาย (Sell)

    # หาจุดเปลี่ยนสัญญาณเพื่อแสดง Marker บนกราฟ
    df["Position"] = df["Signal"].diff()

    # สร้างกราฟ Plotly
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["price"],
            mode="lines",
            name="Price",
            line=dict(color="cyan", width=1.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["SMA_Short"],
            mode="lines",
            name=f"SMA {short_window}",
            line=dict(color="orange", width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["SMA_Long"],
            mode="lines",
            name=f"SMA {long_window}",
            line=dict(color="magenta", width=1),
        )
    )

    # จุดซื้อ (Buy Signals)
    buy_signals = df[df["Position"] == 2]
    fig.add_trace(
        go.Scatter(
            x=buy_signals["timestamp"],
            y=buy_signals["price"],
            mode="markers",
            name="Buy Signal",
            marker=dict(color="green", size=10, symbol="triangle-up"),
        )
    )

    # จุดขาย (Sell Signals)
    sell_signals = df[df["Position"] == -2]
    fig.add_trace(
        go.Scatter(
            x=sell_signals["timestamp"],
            y=sell_signals["price"],
            mode="markers",
            name="Sell Signal",
            marker=dict(color="red", size=10, symbol="triangle-down"),
        )
    )

    fig.update_layout(
        title=f"Hybrid Strategy Backtest: {coin_id.upper()} ({vs_currency.upper()})",
        xaxis_title="Time",
        yaxis_title=f"Price ({vs_currency.upper()})",
        template="plotly_dark",
    )

    latest_status = (
        f"เหรียญ: {coin_id.upper()} | "
        f"ราคาล่าสุด: {df['price'].iloc[-1]:,.2f} {vs_currency.upper()} | "
        f"สถานะกลยุทธ์ปัจจุบัน: {'BUY (สัญญาณซื้อ/ถือเหรียญ)' if df['Signal'].iloc[-1] == 1 else 'SELL (สัญญาณขาย/ถือเงินสด)'}"
    )
    return fig, latest_status

  except Exception as e:
    return None, f"เกิดข้อผิดพลาด: {e}"


# สร้างหน้าตาเว็บแอปด้วย Gradio
with gr.Blocks() as demo:
  gr.Markdown("# 🤖 AI & Hybrid Trading Strategy Backtest Dashboard")
  gr.Markdown(
      "ระบบจำลองกลยุทธ์การเทรดแบบผสมผสาน คำนวณสัญญาณอัตโนมัติบน Hugging Face"
      " Spaces"
  )

  with gr.Row():
    coin_input = gr.Dropdown(
        choices=["bitcoin", "ethereum", "solana", "ripple", "cardano"],
        value="bitcoin",
        label="เลือกเหรียญ (Coin ID)",
    )
    currency_input = gr.Dropdown(
        choices=["usd", "thb"], value="usd", label="สกุลเงินเทียบ"
    )

  with gr.Row():
    short_w = gr.Slider(
        minimum=3, maximum=20, value=5, step=1, label="Short SMA Period"
    )
    long_w = gr.Slider(
        minimum=10, maximum=50, value=20, step=1, label="Long SMA Period"
    )

  btn = gr.Button("รันกลยุทธ์และวิเคราะห์สัญญาณ", variant="primary")

  status_output = gr.Textbox(label="สถานะและผลลัพธ์ล่าสุด")
  plot_output = gr.Plot(label="กราฟแสดงสัญญาณซื้อ/ขาย (Backtest Chart)")

  btn.click(
      fn=run_hybrid_trading_strategy,
      inputs=[coin_input, currency_input, short_w, long_w],
      outputs=[plot_output, status_output],
  )

if __name__ == "__main__":
  demo.launch(theme=gr.themes.Soft())
  
