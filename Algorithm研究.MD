這是一段 100行內的 ETF-NAV / Pair Trading 統計套利範例，較接近現代量化交易研究用途：

import yfinance as yf
import pandas as pd
import numpy as np

# Highly correlated ETFs
symbols = ["SPY", "IVV"]

# Download data
prices = yf.download(
    symbols,
    period="2y",
    auto_adjust=True,
    progress=False
)["Close"].dropna()

# Calculate spread
x = prices["SPY"]
y = prices["IVV"]

beta = np.polyfit(y, x, 1)[0]
spread = x - beta * y

# Rolling z-score
lookback = 30
mean = spread.rolling(lookback).mean()
std = spread.rolling(lookback).std()

z = (spread - mean) / std

# Signal generation
signal = pd.Series(0, index=z.index)

signal[z < -2] = 1      # Long spread
signal[z > 2] = -1      # Short spread
signal[np.abs(z) < 0.5] = 0

signal = signal.replace(0, np.nan).ffill().fillna(0)

# Strategy returns
r1 = x.pct_change()
r2 = y.pct_change()

returns = signal.shift(1) * (r1 - beta * r2)
returns = returns.fillna(0)

equity = (1 + returns).cumprod()

# Metrics
total_return = equity.iloc[-1] - 1
sharpe = np.sqrt(252) * returns.mean() / returns.std()

print("Total Return :", round(total_return * 100, 2), "%")
print("Sharpe Ratio :", round(sharpe, 2))
print("Current ZScore :", round(z.iloc[-1], 2))

if z.iloc[-1] > 2:
    print("Latest Signal : SHORT SPY / LONG IVV")

elif z.iloc[-1] < -2:
    print("Latest Signal : LONG SPY / SHORT IVV")

else:
    print("Latest Signal : NEUTRAL")

核心邏輯
找兩個高度相關資產（SPY、IVV）。
計算 Hedge Ratio（β）。
建立 Spread。
利用 Z-Score 判斷偏離程度。
超過 ±2σ 開倉。
回歸均值平倉。

這類策略屬於：

Statistical Arbitrage
Mean Reversion
Market Neutral
Pair Trading

如果你做 CFD（黃金、原油、Nasdaq、恒指），目前量化圈更常研究的是：

Kalman Filter Pair Trading
Volatility Arbitrage
Funding Rate Arbitrage
Cross-Asset Momentum
Machine Learning Signal Models
Order Flow Imbalance


其中 Kalman Filter + ZScore 動態套利 算是近年實務上比固定 β Pair Trading 更進階的版本。
