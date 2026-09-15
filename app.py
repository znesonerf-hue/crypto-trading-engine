import requests
import pandas as pd
import gradio as gr
import spaces
from datetime import datetime

@spaces.GPU
def analyze_market():
    try:
        # ดึงข้อมูลราคาผ่าน CoinGecko API โดยตรง (ไม่ติดบล็อก IP 451)
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url).json()
        
        btc_price = response['bitcoin']['usd']
        btc_change = response['bitcoin']['usd_24h_change']
        
        eth_price = response['ethereum']['usd']
        eth_change = response['ethereum']['usd_24h_change']
        
        # ระบบวิเคราะห์สัญญาณเบื้องต้นจากเปอร์เซ็นต์เปลี่ยนแปลง 24 ชม.
        if btc_change > 0:
            signal = "🟢 BUY (สัญญาณซื้อ: ตลาดมีทิศทางเป็นบวกใน 24 ชม.ที่ผ่านมา)"
        else:
            signal = "🔴 SELL / HOLD (สัญญาณขายหรือถือรอดูสถานการณ์)"
            
        result = (
            f"--- รายงานตลาดคริปโต (CoinGecko API) --- \n"
            f"เวลาอัปเดต: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🪙 Bitcoin (BTC): ${btc_price:,.2f} (24h Change: {btc_change:.2f}%)\n"
            f"🪙 Ethereum (ETH): ${eth_price:,.2f} (24h Change: {eth_change:.2f}%)\n"
            f"========================================\n"
            f"ผลลัพธ์จากระบบ AI: {signal}"
        )
        return result
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}"

# สร้างหน้าตาเว็บผ่าน Gradio
with gr.Blocks(title="AI Crypto Trading Bot") as demo:
    gr.Markdown("# 🤖 AI Crypto Trading Bot Dashboard")
    gr.Markdown("ระบบวิเคราะห์ตลาดคริปโตเคอร์เรนซีอัตโนมัติ รันบน Hugging Face Spaces (ZeroGPU)")
    
    with gr.Row():
        run_btn = gr.Button("🔄 กดเพื่อรันระบบวิเคราะห์ตลาด", variant="primary")
        
    output_box = gr.Textbox(label="รายงานสถานะและสัญญาณเทรด", lines=8)
    
    run_btn.click(fn=analyze_market, outputs=output_box)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
