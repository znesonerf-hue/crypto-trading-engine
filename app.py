import pandas as pd
import gradio as gr
import spaces  # ZeroGPU decorator for Hugging Face Spaces
from datetime import datetime
from src.connectors.coingecko_connector import CoinGeckoConnector

# Initialize CoinGecko connector
connector = CoinGeckoConnector()

@spaces.GPU  # Use GPU resources on Hugging Face Spaces
def analyze_market(crypto_id: str = 'bitcoin'):
    """
    Analyze cryptocurrency market using CoinGecko API.
    
    Args:
        crypto_id: CoinGecko cryptocurrency ID (e.g., 'bitcoin', 'ethereum')
    
    Returns:
        Market analysis report as string
    """
    try:
        # Get current price
        price_data = connector.get_crypto_price(crypto_id)
        if not price_data:
            return f"❌ Error: Could not fetch data for {crypto_id}. Check if the cryptocurrency ID is correct."
        
        # Get market chart data (7 days)
        market_data = connector.get_market_chart_data(crypto_id, days=7)
        if not market_data or not market_data.prices:
            return f"❌ Error: Could not fetch chart data for {crypto_id}"
        
        # Extract prices and calculate technical indicators
        prices = [p[1] for p in market_data.prices]
        
        # Calculate Simple Moving Averages
        df = pd.DataFrame({'price': prices})
        df['SMA_10'] = df['price'].rolling(window=10).mean()
        df['SMA_50'] = df['price'].rolling(window=min(50, len(prices))].mean()
        
        current_price = prices[-1]
        sma10 = df['SMA_10'].iloc[-1]
        sma50 = df['SMA_50'].iloc[-1]
        
        # Generate trading signal
        if pd.notna(sma10) and pd.notna(sma50):
            if sma10 > sma50:
                signal = "🟢 BUY (Short-term trend stronger than long-term)"
                signal_th = "🟢 ซื้อ (แนวโน้มระยะสั้นแข็งแกร่งกว่าระยะยาว)"
            else:
                signal = "🔴 SELL / HOLD (Short-term weaker than long-term)"
                signal_th = "🔴 ขาย/ถือรอ (แนวโน้มระยะสั้นอ่อนแอกว่าระยะยาว)"
        else:
            signal = "⚪ HOLD (Insufficient data for signal)"
            signal_th = "⚪ ถือรอ (ข้อมูลไม่เพียงพอ)"
        
        # Calculate price change
        price_change = prices[-1] - prices[0]
        price_change_pct = (price_change / prices[0] * 100) if prices[0] > 0 else 0
        
        # Format result
        result = (
            f"{'='*50}\n"
            f"📊 MARKET ANALYSIS REPORT / รายงานการวิเคราะห์ตลาด\n"
            f"{'='*50}\n"
            f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Cryptocurrency: {price_data.name} ({price_data.symbol})\n"
            f"ID: {crypto_id}\n"
            f"\n--- PRICE DATA ---\n"
            f"Current Price: ${current_price:,.2f}\n"
            f"24h Change: ${price_data.price_change_24h:,.2f}\n"
            f"24h Change %: {price_data.price_change_percentage_24h:.2f}%\n"
            f"7-day Change: ${price_change:,.2f} ({price_change_pct:.2f}%)\n"
            f"Market Cap: ${price_data.market_cap:,.0f}\n"
            f"Market Cap Rank: #{price_data.market_cap_rank}\n"
            f"24h Volume: ${price_data.volume_24h:,.0f}\n"
            f"\n--- TECHNICAL INDICATORS (7-day) ---\n"
            f"Current Price: ${current_price:,.2f}\n"
            f"SMA 10: ${sma10:,.2f}\n"
            f"SMA 50: ${sma50:,.2f}\n"
            f"Min Price: ${min(prices):,.2f}\n"
            f"Max Price: ${max(prices):,.2f}\n"
            f"Avg Price: ${sum(prices)/len(prices):,.2f}\n"
            f"\n--- SIGNAL ---\n"
            f"{signal}\n"
            f"{signal_th}\n"
            f"\n--- SUPPLY INFO ---\n"
            f"Circulating Supply: {price_data.circulating_supply:,.0f}\n"
            f"Total Supply: {price_data.total_supply:,.0f}\n"
            f"{'='*50}\n"
            f"📍 Data Source: CoinGecko API (Free Tier)\n"
            f"📡 Running on: Hugging Face Spaces (ZeroGPU)\n"
        )
        
        return result
    
    except Exception as e:
        return f"❌ Error in market analysis: {str(e)}\n\nPlease check:\n- Cryptocurrency ID is correct (e.g., 'bitcoin', 'ethereum')\n- Internet connection\n- CoinGecko API status"

# Build Gradio Interface
with gr.Blocks(title="AI Crypto Trading Bot Dashboard", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 AI Crypto Trading Bot Dashboard
    
    #### ระบบวิเคราะห์ตลาดคริปโตเคอร์เรนซีอัตโนมัติ บน Hugging Face Spaces (ZeroGPU)
    
    **Features / คุณสมบัติ:**
    - ✅ Real-time price data from CoinGecko
    - ✅ 7-day technical analysis (SMA indicators)
    - ✅ Trading signals (Buy/Sell/Hold)
    - ✅ No API keys required
    - ✅ Works worldwide (no geo-restrictions)
    """)
    
    with gr.Row():
        crypto_input = gr.Textbox(
            label="Cryptocurrency ID",
            placeholder="bitcoin, ethereum, cardano, ripple, solana...",
            value="bitcoin",
            info="Use CoinGecko cryptocurrency ID (lowercase)"
        )
    
    with gr.Row():
        analyze_btn = gr.Button("🔍 Analyze Market / วิเคราะห์ตลาด", variant="primary", scale=1)
    
    with gr.Row():
        output_box = gr.Textbox(
            label="📊 Analysis Report / รายงานการวิเคราะห์",
            lines=20,
            max_lines=30
        )
    
    # Connect button to analysis function
    analyze_btn.click(
        fn=analyze_market,
        inputs=crypto_input,
        outputs=output_box
    )
    
    # Add examples
    gr.Examples(
        examples=[
            ["bitcoin"],
            ["ethereum"],
            ["cardano"],
            ["ripple"],
            ["solana"],
            ["dogecoin"]
        ],
        inputs=crypto_input,
        outputs=output_box,
        fn=analyze_market,
        label="Quick Examples / ตัวอย่างด่วน"
    )
    
    gr.Markdown("""
    ---
    
    ### ℹ️ Information / ข้อมูล:
    
    **Data Source:** [CoinGecko API](https://www.coingecko.com/en/api) (Free, No API Key Required)
    
    **Updates:** ~30 seconds delay from real-time
    
    **Rate Limits:** 10-50 requests/minute (free tier)
    
    **Status:** Running on Hugging Face Spaces with ZeroGPU
    
    ---
    
    ### 🚀 How to Use / วิธีใช้:
    
    1. Enter cryptocurrency ID (e.g., bitcoin, ethereum)
    2. Click "Analyze Market" button
    3. View technical analysis and trading signals
    4. Signals: 🟢 BUY | 🔴 SELL/HOLD | ⚪ HOLD
    
    ### ⚠️ Disclaimer:
    
    This is for **educational and analysis purposes only**. Not financial advice. Always do your own research (DYOR) before trading.
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
