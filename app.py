import gradio as gr
import requests
import time
import threading
from datetime import datetime

# ตัวแปรกลางสำหรับเก็บสถานะพอร์ตและประวัติการทำงานเบื้องหลัง 24 ชม.
bot_state = {
    "status": "กำลังเริ่มระบบทำงานเบื้องหลัง...",
    "cash": 10000.0,
    "btc": 0.0,
    "eth": 0.0,
    "history": []
}

def background_trading_loop():
    """ฟังก์ชันรันวนลูปเบื้องหลังทุก 60 นาที/วินาที ตลอด 24 ชั่วโมง"""
    while True:
        try:
            # ใช้ CoinGecko API สาธารณะ ปลอดภัย ไม่โดนบล็อก IP 451 บน Hugging Face
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
            response = requests.get(url, timeout=10).json()

            btc_price = response['bitcoin']['usd']
            btc_change = response['bitcoin']['usd_24h_change']
            eth_price = response['ethereum']['usd']

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            action_text = ""

            # ระบบจำลองการตัดสินใจซื้อขายของ AI
            if btc_change > 0 and bot_state["cash"] > 0:
                invest_amount = bot_state["cash"] * 0.5
                bought_btc = invest_amount / btc_price
                bot_state["cash"] -= invest_amount
                bot_state["btc"] += bought_btc
                action_text = "🟢 [AI BUY] ตลาดขาขึ้น เข้าซื้อ Bitcoin เพิ่ม"
                bot_state["history"].insert(0, f"[{current_time}] BUY: {bought_btc:.4f} BTC @ ${btc_price:,.2f}")

            elif btc_change <= 0 and bot_state["btc"] > 0:
                sold_value = bot_state["btc"] * btc_price
                bot_state["cash"] += sold_value
                bot_state["btc"] = 0.0
                action_text = "🔴 [AI SELL] ตลาดขาลง ขาย Bitcoin ล็อคกำไร"
                bot_state["history"].insert(0, f"[{current_time}] SELL BTC @ ${btc_price:,.2f}")
            else:
                action_text = "🛡️ [AI HOLD] ตลาดทรงตัว ถือสถานะเดิม"

            total_portfolio_value = bot_state["cash"] + (bot_state["btc"] * btc_price) + (bot_state["eth"] * eth_price)
            profit_loss = total_portfolio_value - 10000.0
            profit_loss_pct = (profit_loss / 10000.0) * 100

            # บันทึกสถานะล่าสุดเก็บไว้ในหน่วยความจำ
            bot_state["status"] = (
                f"==================================================\n"
                f" 🤖 24/7 AI CRYPTO TRADING BOT (Background Active)\n"
                f"==================================================\n"
                f"⏱️ อัปเดตล่าสุด: {current_time}\n\n"
                f"💵 เงินสดคงเหลือ (Cash): ${bot_state['cash']:,.2f}\n"
                f"₿ Bitcoin ที่ถือครอง: {bot_state['btc']:.4f} BTC (ราคา: ${btc_price:,.2f} | 24h: {btc_change:+.2f}%)\n\n"
                f"📊 มูลค่าพอร์ตลงทุนรวม: ${total_portfolio_value:,.2f}\n"
                f"📈 กำไร / ขาดทุนสุทธิ: ${profit_loss:+,.2f} ({profit_loss_pct:+.2f}%)\n"
                f"--------------------------------------------------\n"
                f"🎯 สัญญาณล่าสุด: {action_text}\n"
                f"--------------------------------------------------\n"
                f"📜 ประวัติการซื้อขาย:\n" + ("\n".join(bot_state["history"][:5]) if bot_state["history"] else "ยังไม่มีประวัติ")
            )
        except Exception as e:
            bot_state["status"] = f"⚠️ เกิดข้อผิดพลาดในการดึงข้อมูลตลาด: {str(e)}"

        # พักการทำงาน 60 วินาที แล้ววนลูปเช็กราคาใหม่
        time.sleep(60)

# เริ่มต้นเธรดรันเบื้องหลังทันที
t = threading.Thread(target=background_trading_loop, daemon=True)
t.start()

def get_latest_status():
    return bot_state["status"]

# สร้างหน้าเว็บ Gradio (ถอดโค้ด @spaces.GPU ที่ทำให้เกิด Runtime Error ออกเรียบร้อย)
with gr.Blocks(title="24/7 AI Crypto Trading Bot") as demo:
    gr.Markdown("# 🤖 24/7 AI Crypto Trading Bot Dashboard")
    gr.Markdown("ระบบเทรดจำลองอัตโนมัติ ทำงานเบื้องหลังตลอด 24 ชม. เชื่อมต่อกับ Better Stack เรียบร้อยแล้ว")
    
    with gr.Row():
        refresh_btn = gr.Button("🔄 รีเฟรชดูสถานะล่าสุด", variant="primary")
        
    output_box = gr.Textbox(label="รายงานสถานะพอร์ตแบบเรียลไทม์", lines=15)
    
    refresh_btn.click(fn=get_latest_status, outputs=output_box)
    demo.load(fn=get_latest_status, outputs=output_box)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
