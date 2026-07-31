import pandas as pd

def calculate_macd(df: pd.DataFrame, span_short: int = 12, span_long: int = 26, span_signal: int = 9) -> pd.DataFrame:
    """
    คำนวณค่า MACD (Moving Average Convergence Divergence)
    """
    df['EMA_short'] = df['close'].ewm(span=span_short, adjust=False).mean()
    df['EMA_long'] = df['close'].ewm(span=span_long, adjust=False).mean()
    df['MACD'] = df['EMA_short'] - df['EMA_long']
    df['Signal_Line'] = df['MACD'].ewm(span=span_signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal_Line']
    return df

def calculate_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    คำนวณค่า RSI (Relative Strength Index)
    """
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def calculate_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """
    คำนวณค่า Bollinger Bands (Middle, Upper, Lower)
    """
    df['BB_Middle'] = df['close'].rolling(window=window).mean()
    std = df['close'].rolling(window=window).std()
    df['BB_Upper'] = df['BB_Middle'] + (std * num_std)
    df['BB_Lower'] = df['BB_Middle'] - (std * num_std)
    return df
    
