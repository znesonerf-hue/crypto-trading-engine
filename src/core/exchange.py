import requests
import time

# ฟังก์ชันดึงราคาปัจจุบันจาก CoinGecko API
def get_coingecko_price(coin_id="bitcoin", vs_currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}"
    headers = {
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        price = data[coin_id][vs_currency]
        return price
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลราคา: {e}")
        return None

# คลาสสำหรับระบบจำลองการเทรด (Paper Trading Portfolio)
class PaperTradingSimulator:
    def __init__(self, starting_cash=10000.0):
        self.cash = starting_cash
        self.crypto_balance = 0.0
        
    def buy(self, coin_id, amount_usd):
        price = get_coingecko_price(coin_id)
        if price is None:
            print("❌ ไม่สามารถดึงราคาปัจจุบันได้")
            return
            
        if self.cash >= amount_usd:
            amount_crypto = amount_usd / price
            self.cash -= amount_usd
            self.crypto_balance += amount_crypto
            print(f"✅ [Paper Buy] ซื้อ {coin_id.upper()} สำเร็จ!")
            print(f"   - ราคาซื้อ: ${price:,.2f}")
            print(f"   - จำนวนที่ได้: {amount_crypto:.6f} {coin_id.upper()}")
            print(f"   - เงินสดคงเหลือ: ${self.cash:,.2f}\n")
        else:
            print("❌ ยอดเงินสดในพอร์ตจำลองไม่เพียงพอ\n")
            
    def sell(self, coin_id, amount_crypto):
        price = get_coingecko_price(coin_id)
        if price is None:
            print("❌ ไม่สามารถดึงราคาปัจจุบันได้")
            return
            
        if self.crypto_balance >= amount_crypto:
            revenue = amount_crypto * price
            self.crypto_balance -= amount_crypto
            self.cash += revenue
            print(f"✅ [Paper Sell] ขาย {coin_id.upper()} สำเร็จ!")
            print(f"   - ราคาขาย: ${price:,.2f}")
            print(f"   - ได้รับเงินสด: ${revenue:,.2f}")
            print(f"   - เงินสดคงเหลือ: ${self.cash:,.2f}\n")
        else:
            print("❌ จำนวนเหรียญในพอร์ตจำลองไม่เพียงพอ\n")
            
    def portfolio_status(self, coin_id):
        price = get_coingecko_price(coin_id)
        if price is None:
            return
            
        total_crypto_value = self.crypto_balance * price
        total_portfolio_value = self.cash + total_crypto_value
        
        print("="*45)
        print("📊 สถานะพอร์ตจำลอง (Paper Trading Portfolio)")
        print("="*45)
        print(f" - ราคาปัจจุบันของ {coin_id.upper()}: ${price:,.2f}")
        print(f" - เงินสด (Cash): ${self.cash:,.2f}")
        print(f" - จำนวนเหรียญในพอร์ต: {self.crypto_balance:.6f}")
        print(f" - มูลค่ารวมของพอร์ต: ${total_portfolio_value:,.2f}")
        print("="*45 + "\n")

# --- ตัวอย่างการใช้งานโปรแกรม ---
if __name__ == "__main__":
    # เริ่มต้นจำลองพอร์ตด้วยเงิน 50,000 ดอลลาร์
    paper_bot = PaperTradingSimulator(starting_cash=50000.0)
    
    # 1. เช็คสถานะพอร์ตเริ่มต้น
    paper_bot.portfolio_status("bitcoin")
    
    # 2. จำลองคำสั่งซื้อ Bitcoin มูลค่า $10,000
    print("กำลังส่งคำสั่งซื้อ Bitcoin...")
    paper_bot.buy("bitcoin", 10000.0)
    
    # 3. เช็คสถานะพอร์ตหลังซื้อ
    paper_bot.portfolio_status("bitcoin")
        
