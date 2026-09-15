import requests
import pandas as pd
import gradio as gr
import spaces
from datetime import datetime

# เก็บสถานะ Portfolio จำลอง (เงินเริ่มต้น $10,000)
portfolio = {
    "cash": 10000.0,
    "btc": 0.0,
    "eth": 0.0,
    "history": []
}

@spaces.GPU
def paper_trade_bot():
    global portfolio
    try:
        # ดึงราคาปัจจุบันจาก CoinGecko
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url).json()
        
        btc_price = response['bitcoin']['usd']
        btc_change = response['bitcoin']['usd_24h_change']
        
        eth_price = response['ethereum']['usd']
        eth_change = response['ethereum']['usd_24h_change']
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        action_text = ""
        
        # เงื่อนไข AI จำลองการเทรด: ถ้า 24h change เป็นบวกและมีเงินสด -> ซื้อ BTC, ถ้าติดลบ -> ขายออกเป็นเงินสด
        if btc_change > 0 and portfolio["cash"] > 1000:
            invest_amount = portfolio["cash"] * 0.5  # ใช้เงิน 50% ของที่มีซื้อ
            bought_btc = invest_amount / btc_price
            portfolio["cash"] -= invest_amount
            portfolio["btc"] += bought_btc
            action_text = f"🟢 [BUY] ซื้อ BTC จำนวน {bought_btc:.4f} ที่ราคา ${btc_price:,.2f}"
            portfolio["history"].insert(0, f"[{current_time}] {action_text}")
            
        elif btc_change <= 0 and portfolio["btc"] > 0:
            sold_value = portfolio["btc"] * btc_price
            portfolio["cash"] += sold_value
            action_text = f"🔴 [SELL] ขาย BTC ทั้งหมด ได้เงิน ${sold_value:,.2f} ที่ราคา ${btc_price:,.2f}"
            portfolio["btc"] = 0.0
            portfolio["history"].insert(0, f"[{current_time}] {action_text}")
        else:
            action_text = "⚪ [HOLD] ถือสถานะเดิม (รอจังหวะตลาด)"

        # คำนวณมูลค่าพอร์ตทั้งหมด
        total_portfolio_value = portfolio["cash"] + (portfolio["btc"] * btc_price) + (portfolio["eth"] * eth_price)
        profit_loss = total_portfolio_value - 10000.0
        profit_loss_pct = (profit_loss / 10000.0) * 100

        report = (
            f"📊 --- AI Crypto Paper Trading Dashboard --- \n"
            f"เวลาอัปเดต: {current_time}\n\n"
            f"💵 เงินสดในพอร์ต (Cash): ${portfolio['cash']:,.2f}\n"
            f"🪙 Bitcoin ที่ถือ: {portfolio['btc']:.4f} BTC (มูลค่า: ${portfolio['btc'] * btc_price:,.2f})\n"
            f"🪙 Ethereum ที่ถือ: {portfolio['eth']:.4f} ETH (มูลค่า: ${portfolio['eth'] * eth_price:,.2f})\n"
            f"----------------------------------------\n"
            f"💰 มูลค่าพอร์ตสุทธิทั้งหมด: ${total_portfolio_value:,.2f}\n"
            f"📈 กำไร/ขาดทุนรวม: ${profit_loss:+,.2f} ({profit_loss_pct:+.2f}%)\n"
            f"========================================\n"
            f"🤖 การตัดสินใจรอบนี้: {action_text}\n\n"
            f"📜 ประวัติการเทรดจำลอง:\n" + ("\n".join(portfolio["history"][:5]) if portfolio["history"] else "ยังไม่มีประวัติการเทรด")
        )
        return report
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {str(e)}"

# สร้างหน้าเว็บ Gradio
with gr.Blocks(title="AI Crypto Paper Trading Bot") as demo:
    gr.Markdown("# 🤖 AI Crypto Paper Trading Bot")
    gr.Markdown("ระบบจำลองเทรดคริปโตอัตโนมัติด้วยเงินจำลองเริ่มต้น $10,000 USD บน Hugging Face Spaces")
    
    with gr.Row():
        run_btn = gr.Button("🔄 รันระบบ Paper Trade (อัปเดตพอร์ต)", variant="primary")
        
    output_box = gr.Textbox(label="รายงานสถานะพอร์ตจำลองและประวัติการเทรด", lines=16)
    
    run_btn.click(fn=paper_trade_bot, outputs=output_box)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
