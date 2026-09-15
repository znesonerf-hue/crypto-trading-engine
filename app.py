import gradio as gr
import requests
import time
import threading
from datetime import datetime

# ตัวแปรเก็บสถานะพอร์ต
bot_state = {
    "status": "กำลังเชื่อมต่อและดึงข้อมูลตลาดรอบแรก...",
    "cash": 10000.0,
    "btc": 0.0,
    "eth": 0.0,
    "history": []
}

def fetch_market_data():
    """ฟังก์ชันดึงราคาและประมวลผลการเทรด"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=10).json()

        btc_price = response['bitcoin']['usd']
        btc_change = response['bitcoin']['usd_24h_change']
        eth_price = response['ethereum']['usd']

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        action_text = ""

        # ระบบตัดสินใจจำลองของ AI
        if btc_change > 0 and bot_state["cash"] > 0:
            invest_amount = bot_state["cash"] * 0.5
            bought_btc = invest_amount / btc_price
            bot_state["cash"] -= invest_amount
            bot_state["btc"] += bought_btc
            action_text = "🟢 [AI BUY] ตลาดบวก เข้าซื้อ Bitcoin เพิ่ม"
            bot_state["history"].insert(0, f"[{current_time}] BUY: {bought_btc:.4f} BTC @ ${btc_price:,.2f}")

        elif btc_change <= 0 and bot_state["btc"] > 0:
            sold_value = bot_state["btc"] * btc_price
            bot_state["cash"] += sold_value
            bot_state["btc"] = 0.0
            action_text = "🔴 [AI SELL] ตลาดลบ ขาย Bitcoin ถือเงินสด"
            bot_state["history"].insert(0, f"[{current_time}] SELL BTC @ ${btc_price:,.2f}")
        else:
            action_text = "🛡️ [AI HOLD] ตลาดทรงตัว ถือสถานะเดิม"

        total_portfolio_value = bot_state["cash"] + (bot_state["btc"] * btc_price) + (bot_state["eth"] * eth_price)
        profit_loss = total_portfolio_value - 10000.0
        profit_loss_pct = (profit_loss / 10000.0) * 100

        # อัปเดตข้อความแสดงผล
        bot_state["status"] = (
            f"==================================================\n"
            f" 🤖 24/7 AI CRYPTO TRADING BOT (Running Background)\n"
            f"==================================================\n"
            f"⏱️ อัปเดตล่าสุด: {current_time}\n\n"
            f"💵 เงินสดคงเหลือ (Cash): ${bot_state['cash']:,.2f}\n"
            f"₿ Bitcoin ที่ถือครอง: {bot_state['btc']:.4f} BTC (ราคา: ${btc_price:,.2f} | 24h: {btc_change:+.2f}%)\n\n"
            f"📊 มูลค่าพอร์ตลงทุนรวม: ${total_portfolio_value:,.2f}\n"
            f"📈 กำไร / ขาดทุนสุทธิ: ${profit_loss:+,.2f} ({profit_loss_pct:+.2f}%)\n"
            f"--------------------------------------------------\n"
            f"🎯 การทำงานล่าสุด: {action_text}\n"
            f"--------------------------------------------------\n"
            f"📜 ประวัติการทำรายการ:\n" + ("\n".join(bot_state["history"][:5]) if bot_state["history"] else "ยังไม่มีประวัติ")
        )
    except Exception as e:
        bot_state["status"] = f"⚠️ กำลังเชื่อมต่อใหม่ หรือเกิดข้อผิดพลาด: {str(e)}"

def background_trading_loop():
    # ดึงข้อมูลทันทีเมื่อเริ่มรันโปรแกรมครั้งแรก
    fetch_market_data()
    while True:
        time.sleep(60)  # วนลูปทุกๆ 60 วินาที
        fetch_market_data()

# เริ่มต้นเธรดทำงานเบื้องหลัง
t = threading.Thread(target=background_trading_loop, daemon=True)
t.start()

def get_latest_status():
    return bot_state["status"]

# สร้างหน้าเว็บ Gradio
with gr.Blocks(title="24/7 AI Crypto Trading Bot") as demo:
    gr.Markdown("# 🤖 AI Crypto Trading Bot (Running 24/7)")
    gr.Markdown("บอทกำลังทำงานประมวลผลเบื้องหลังตลอด 24 ชั่วโมง ข้อมูลจะอัปเดตให้อัตโนมัติ")
    
    with gr.Row():
        refresh_btn = gr.Button("🔄 รีเฟรชหน้าจอเพื่อดูสถานะล่าสุด", variant="primary")
        
    output_box = gr.Textbox(label="รายงานสถานะพอร์ตและสัญญาณ AI แบบเรียลไทม์", lines=15)
    
    refresh_btn.click(fn=get_latest_status, outputs=output_box)
    demo.load(fn=get_latest_status, outputs=output_box)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
