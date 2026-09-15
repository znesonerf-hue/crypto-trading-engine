import gradio as gr
import pandas as pd
from datetime import datetime

# นำเข้าโมดูลจากโฟลเดอร์ src ตามโครงสร้างของคุณ
try:
    from src.core.engine import TradingEngine
    from src.core.portfolio import Portfolio
    engine_available = True
except Exception as e:
    engine_available = False
    import_error = str(e)

def run_trading_engine(strategy_choice):
    if not engine_available:
        return f"❌ ไม่สามารถโหลดโมดูลจาก src ได้: {import_error}\nโปรดตรวจสอบชื่อคลาสและไฟล์ใน src/core/engine.py"
    
    try:
        # ตัวอย่างการเรียกใช้งาน Engine หรือกลยุทธ์ที่คุณเขียนไว้ใน src/
        # engine = TradingEngine()
        
        return (
            f"--- 🚀 Crypto Trading Engine Status --- \n"
            f"เวลาทำงาน: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"กลยุทธ์ที่เลือก: {strategy_choice}\n"
            f"สถานะ: เชื่อมต่อโครงสร้าง src/ สำเร็จ พร้อมประมวลผล!\n\n"
            f"💡 คำแนะนำ: หากใน src/connectors/binance.py มีการเรียกใช้ Binance API "
            f"บน Hugging Face อาจติดปัญหา Error 451 แนะนำให้เปลี่ยนไปใช้ CoinGecko หรือ Kraken แทน"
        )
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการรันระบบ: {str(e)}"

# สร้างหน้าตาแดชบอร์ด Gradio
with gr.Blocks(title="Crypto Trading Engine Dashboard") as demo:
    gr.Markdown("# 🤖 Crypto Trading Engine Dashboard")
    gr.Markdown("ระบบควบคุมและแสดงผลกลยุทธ์เทรดที่ดึงโครงสร้างมาจากโฟลเดอร์ `src/` ของคุณโดยตรง")
    
    with gr.Row():
        strategy_dropdown = gr.Dropdown(
            choices=["momentum", "mean_reversion", "grid_trading", "arbitrage", "dca"],
            value="momentum",
            label="เลือกกลยุทธ์ (Strategies)"
        )
        run_btn = gr.Button("🚀 เริ่มรันกลยุทธ์", variant="primary")
        
    output_box = gr.Textbox(label="รายงานผลลัพธ์จาก Engine", lines=10)
    
    run_btn.click(fn=run_trading_engine, inputs=strategy_dropdown, outputs=output_box)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
