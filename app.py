import gradio as gr 
import pandas as pd
import plotly.graph_objects as go
import requests
import spaces


@spaces.GPU
def analyze_minute_trade(coin_id, vs_currency):
  try:
    # ดึงข้อมูล 1 วันล่าสุด (ความละเอียดสูงสุดของ CoinGecko ฟรี คือประมาณทุกๆ 5 นาที)
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": "1"}
    response = requests.get(url, params=params)
    data = response.json()

    if "prices" not in data:
      return None, f"ไม่สามารถดึงข้อมูลได้: {data.get('status', 'Rate limit')}"

    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # ใช้ Exponential Moving Average (EMA) แบบเร็ว สำหรับกรอบเวลานั้นๆ
    df["EMA_Fast"] = df["price"].ewm(span=3, adjust=False).mean()
    df["EMA_Slow"] = df["price"].ewm(span=8, adjust=False).mean()

    # คำนวณสัญญาณซื้อขายระยะสั้น
    df["Signal"] = 0
    df.loc[df["EMA_Fast"] > df["EMA_Slow"], "Signal"] = 1
    df.loc[df["EMA_Fast"] <= df["EMA_Slow"], "Signal"] = -1
    df["Position"] = df["Signal"].diff()

    # สร้างกราฟ Plotly
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["price"],
            mode="lines",
            name="Price (Intraday)",
            line=dict(color="cyan", width=1.5),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["EMA_Fast"],
            mode="lines",
            name="EMA 3 (Fast)",
            line=dict(color="orange", width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["EMA_Slow"],
            mode="lines",
            name="EMA 8 (Slow)",
            line=dict(color="magenta", width=1),
        )
    )

    # จุดซื้อระยะสั้น
    buy_signals = df[df["Position"] == 2]
    fig.add_trace(
        go.Scatter(
            x=buy_signals["timestamp"],
            y=buy_signals["price"],
            mode="markers",
            name="Scalp Buy",
            marker=dict(color="green", size=9, symbol="triangle-up"),
        )
    )

    # จุดขายระยะสั้น
    sell_signals = df[df["Position"] == -2]
    fig.add_trace(
        go.Scatter(
            x=sell_signals["timestamp"],
            y=sell_signals["price"],
            mode="markers",
            name="Scalp Sell",
            marker=dict(color="red", size=9, symbol="triangle-down"),
        )
    )

    fig.update_layout(
        title=f"Intraday Scalping View: {coin_id.upper()} ({vs_currency.upper()})",
        xaxis_title="Time (Last 24 Hours)",
        yaxis_title=f"Price ({vs_currency.upper()})",
        template="plotly_dark",
    )

    status = (
        f"เหรียญ: {coin_id.upper()} | ราคาปัจจุบัน: {df['price'].iloc[-1]:,.2f}"
        f" {vs_currency.upper()} | สัญญาณระยะสั้น: {'LONG / BUY' if df['Signal'].iloc[-1] == 1 else 'SHORT / SELL'}"
    )
    return fig, status

  except Exception as e:
    return None, f"เกิดข้อผิดพลาด: {e}"


# สร้างหน้า UI ด้วย Gradio
with gr.Blocks() as demo:
  gr.Markdown("# ⚡ Intraday & Scalping Analysis Dashboard")
  gr.Markdown(
      "จำลองการวิเคราะห์ข้อมูลความถี่สูงระยะสั้น (24 ชั่วโมงล่าสุด) ด้วย EMA"
      " ระยะสั้น"
  )

  with gr.Row():
    coin_input = gr.Dropdown(
        choices=["bitcoin", "ethereum", "solana", "ripple"],
        value="bitcoin",
        label="เลือกเหรียญ",
    )
    currency_input = gr.Dropdown(
        choices=["usd", "thb"], value="usd", label="สกุลเงิน"
    )

  btn = gr.Button("วิเคราะห์กราฟระยะสั้น", variant="primary")

  status_output = gr.Textbox(label="สถานะตลาดระยะสั้น")
  plot_output = gr.Plot(label="กราฟสัญญาณเทรดระยะสั้น")

  btn.click(
      fn=analyze_minute_trade,
      inputs=[coin_input, currency_input],
      outputs=[plot_output, status_output],
  )

if __name__ == "__main__":
  demo.launch(theme=gr.themes.Soft())
  
