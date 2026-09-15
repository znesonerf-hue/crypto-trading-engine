import threading
import time
import streamlit as st

# ฟังก์ชันบอทเทรดของคุณ (รันเบื้องหลัง)
def trading_bot_loop():
    while True:
        try:
            print("Bot is checking market and trading...")
            # ใส่โค้ด CCXT หรือระบบเทรดของคุณตรงนี้
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)

# ป้องกันไม่ให้เธรดถูกสร้างซ้ำเวลาหน้าเว็บรีเฟรช
if "bot_running" not in st.session_state:
    st.session_state.bot_running = True
    bot_thread = threading.Thread(target=trading_bot_loop, daemon=True)
    bot_thread.start()

# หน้าตา Dashboard บนเว็บ Streamlit
st.title("🤖 Automated Crypto Trading Bot")
st.write("Status: **Running 24/7**")
st.info("Bot is active in the background.")
