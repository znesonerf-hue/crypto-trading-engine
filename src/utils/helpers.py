import pandas as pd

def calculate_macd(df: pd.DataFrame, span_short: int = 12, span_long: int = 26, span_signal: int = 9) -> pd.DataFrame:
    """
    คำนวณค่า MACD (Moving Average Convergence Divergence) เบื้องต้น
    """
    df['EMA_short'] = df['close'].ewm(span=span_short, adjust=False).mean()
    df['EMA_long'] = df['close'].ewm(span=span_long, adjust=False).mean()
    df['MACD'] = df['EMA_short'] - df['EMA_long']
    df['Signal_Line'] = df['MACD'].ewm(span=span_signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal_Line']
    return df
  
