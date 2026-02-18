# macd_peak_sell.py
# 簡單 MACD 頂峰回落賣出策略 (僅示範邏輯，非實戰完整版)
# 需要安裝: pip install pandas pandas_ta yfinance scipy

import pandas as pd
import yfinance as yf
from scipy.signal import argrelextrema
import numpy as np
# from pandas_ta.momentum import macd  # 或用 talib

# ================== 參數 ==================
SYMBOL = "GC=F"          # 黃金期貨，或改成 "XAUUSD=X" / "AAPL" 等
INTERVAL = "1d"          # 1d, 4h, 1h 等
LOOKBACK = 500           # 取最近多少根K線
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
PEAK_ORDER = 5           # 找局部極大值時左右看幾根 (越大越嚴格)

# ================== 下載數據 ==================
print(f"下載 {SYMBOL} 數據...")
df = yf.download(SYMBOL, period="max", interval=INTERVAL)[-LOOKBACK:]
df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()

# ================== 計算 MACD ==================
# 用 pandas_ta (推薦) 或 talib
try:
    macd = df.ta.macd(fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    df['macd']     = macd['MACD_12_26_9']
    df['signal']   = macd['MACDs_12_26_9']
    df['hist']     = macd['MACDh_12_26_9']
except:
    # 若無 pandas_ta，用簡單 EMA 計算 (近似)
    ema_fast = df['Close'].ewm(span=MACD_FAST, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=MACD_SLOW, adjust=False).mean()
    df['macd']   = ema_fast - ema_slow
    df['signal'] = df['macd'].ewm(span=MACD_SIGNAL, adjust=False).mean()
    df['hist']   = df['macd'] - df['signal']

# ================== 找 MACD hist 頂峰回落 ==================
# 用 argrelextrema 找局部最大值 (頂峰)
hist = df['hist'].values
peaks_idx = argrelextrema(hist, np.greater, order=PEAK_ORDER)[0]

# 只保留最近的頂峰 (避免太舊的)
recent_peaks = peaks_idx[peaks_idx > len(df)-60]  # 最近60根內的頂峰

trades = []
position = False  # 是否持倉

for i in range(1, len(df)):
    row = df.iloc[i]
    prev = df.iloc[i-1]
    
    # 進場條件：可自訂，例如 MACD 金叉 或 hist > 0 等
    # 這裡簡單用 hist 由負轉正作為買入條件
    if not position:
        if prev['hist'] < 0 and row['hist'] > 0:
            print(f"{row.name.date()} 買入 @ {row['Close']:.2f}")
            trades.append(('BUY', row.name, row['Close']))
            position = True
    
    # 出場條件：MACD hist 從頂峰回落
    if position:
        # 檢查是否剛經過一個頂峰且開始回落
        if i-1 in recent_peaks and row['hist'] < prev['hist']:
            print(f"{row.name.date()} 賣出(頂峰回落) @ {row['Close']:.2f}")
            trades.append(('SELL', row.name, row['Close']))
            position = False

# 若最後還持倉，強制平倉
if position:
    last = df.iloc[-1]
    print(f"{last.name.date()} 最後平倉 @ {last['Close']:.2f}")
    trades.append(('SELL', last.name, last['Close']))

# ================== 簡單績效 ==================
if len(trades) >= 2:
    profit = 0
    for j in range(0, len(trades), 2):
        if j+1 < len(trades):
            buy_p = trades[j][2]
            sell_p = trades[j+1][2]
            profit += (sell_p - buy_p)
    print(f"\n總交易次數: {len(trades)//2}")
    print(f"淨利 (未扣手續費): {profit:.2f} ({profit/buy_p*100:.2f}%)")

print("\n腳本結束。建議結合其他濾波條件（如趨勢、RSI）再實戰。")