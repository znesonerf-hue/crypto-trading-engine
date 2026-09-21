import gradio as gr
import pandas as pd
import plotly.graph_objects as go
import requests
import spaces


# ใช้ @spaces.GPU ร่วมกับ ZeroGPU บน Hugging Face
@spaces.GPU
def get_coingecko_data(coin_id, vs_currency):
  try:
    # ดึงข้อมูลราคาย้อนหลัง 1 วันจาก CoinGecko Public API
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": "1"}
    response = requests.get(url, params=params)
    data = response.json()

    if "prices" not in data:
      return (
          None,
          f"ไม่สามารถดึงข้อมูลได้ (อาจติด Rate Limit ของ CoinGecko): {data}",
      )

    prices = data["prices"]  # รูปแบบข้อมูล: [[timestamp, price], ...]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

    # คำนวณ Moving Average เบื้องต้น
    df["MA5"] = df["price"].rolling(window=5).mean()

    # สร้างกราฟเส้นด้วย Plotly
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["price"],
            mode="lines",
            name="Price",
            line=dict(color="cyan"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df["MA5"],
            mode="lines",
            name="MA 5",
            line=dict(color="orange"),
        )
    )

    fig.update_layout(
        title=f"CoinGecko Market Data: {coin_id.upper()} ({vs_currency.upper()})",
        xaxis_title="Time",
        yaxis_title=f"Price ({vs_currency.upper()})",
        template="plotly_dark",
    )

    latest_price = (
        f"ราคาล่าสุด ({coin_id.upper()}): {df['price'].iloc[-1]:,.2f}"
        f" {vs_currency.upper()}"
    )
    return fig, latest_price
  except Exception as e:
    return None, f"เกิดข้อผิดพลาด: {e}"


# สร้างหน้าตาเว็บแอปด้วย Gradio
with gr.Blocks() as demo:
  gr.Markdown("# 🦎 CoinGecko Crypto Dashboard with ZeroGPU")
  gr.Markdown("ดึงข้อมูลและกราฟราคาคริปโตแบบเรียลไทม์จาก CoinGecko API")

  with gr.Row():
    coin_input = gr.Dropdown(
        choices=["bitcoin", "ethereum", "solana", "dogecoin", "ripple"],
        value="bitcoin",
        label="เลือกเหรียญ (Coin ID)",
    )
    currency_input = gr.Dropdown(
        choices=["usd", "thb"], value="usd", label="สกุลเงินเทียบ (Currency)"
    )

  btn = gr.Button("โหลดข้อมูลจาก CoinGecko", variant="primary")

  price_output = gr.Textbox(label="สรุปราคาปัจจุบัน")
  plot_output = gr.Plot(label="กราฟราคาทางเทคนิค")

  btn.click(
      fn=get_coingecko_data,
      inputs=[coin_input, currency_input],
      outputs=[plot_output, price_output],
  )

if __name__ == "__main__":
  demo.launch(theme=gr.themes.Soft())
  
