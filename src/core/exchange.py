import requests

class BitkubMarketData:
    def __init__(self):
        self.url = "https://api.bitkub.com/api/v3/market/ticker"

    def get_ticker(self, symbol: str = "THB_BTC"):
        """
        ดึงข้อมูลราคาตลาดล่าสุดจาก Bitkub v3 API
        """
        try:
            response = requests.get(self.url, timeout=10)
            data = response.json()
            
            # ตรวจสอบรูปแบบข้อมูลที่ได้จาก Bitkub
            if isinstance(data, dict) and symbol in data:
                return {
                    "symbol": symbol,
                    "close": float(data[symbol]["last"]),
                    "high": float(data[symbol]["high"]),
                    "low": float(data[symbol]["low"]),
                    "volume": float(data[symbol]["quoteVolume"])
                }
        except Exception as e:
            print(f"Error fetching Bitkub market data: {e}")
            
        return None
      
