import ccxt
import pandas as pd
import gradio as gr
import spaces  # 1. นำเข้าไลบรารี spaces สำหรับ ZeroGPU
from datetime import datetime

@spaces.GPU  # 2. ใส่ Decorator นี้กำกับฟังก์ชันที่ต้องการใช้ทรัพยากร
def analyze_market():
    try:
        exchange = ccxt.binance()
        symbol = 'BTC/USDT'
        
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=50)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        df['SMA_10'] = df['close'].rolling(window=10).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        
        current_price = df['close'].iloc[-1]
        sma10 = df['SMA_10'].iloc[-1]
        sma50 = df['SMA_50'].iloc[-1]
        
        if sma10 > sma50:
            signal = "🟢 BUY (สัญญาณซื้อ: แนวโน้มระยะสั้นแข็งแกร่งกว่าระยะยาว)"
        else:
            signal = "🔴 SELL / HOLD (สัญญาณขายหรือถือรอดูสถานการณ์)"
            
        result = (
            f"--- บันทึกการวิเคราะห์ตลาด --- \n"
            f"เวลาอัปเดต: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"คู่เหรียญ: {symbol}\n"
            f"ราคาปัจจุบัน: {current_price:,.2f} USDT\n"
            f"ค่าเฉลี่ย SMA 10: {sma10:,.2f}\n"
            f"ค่าเฉลี่ย SMA 50: {sma50:,.2f}\n"
            f"========================================\n"
            f"ผลลัพธ์จากระบบ AI: {signal}"
        )
        return result
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการเชื่อมต่อตลาด: {str(e)}"

with gr.Blocks(title="AI Crypto Trading Bot") as demo:
    gr.Markdown("# 🤖 AI Crypto Trading Bot Dashboard")
    gr.Markdown("ระบบวิเคราะห์ตลาดคริปโตเคอร์เรนซีอัตโนมัติ รันบน Hugging Face Spaces (ZeroGPU)")
    
    with gr.Row():
        run_btn = gr.Button("🔄 กดเพื่อรันระบบวิเคราะห์ตลาด", variant="primary")
        
    output_box = gr.Textbox(label="รายงานสถานะและสัญญาณเทรด", lines=8)
    
    run_btn.click(fn=analyze_market, outputs=output_box)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    
