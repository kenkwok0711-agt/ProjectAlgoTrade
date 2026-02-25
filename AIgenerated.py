import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import datetime

# 生成合成股票數據（模擬 AAPL 收盤價）
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', periods=365, freq='D')
prices = np.cumsum(np.random.randn(365) * 2 + 0.1) + 150  # 模擬隨機遊走，從 150 開始
data = pd.DataFrame({'close': prices}, index=dates)

# 創建特徵：使用前幾天的收盤價預測下一天
def create_features(df, lag=5):
    for i in range(1, lag+1):
        df[f'lag_{i}'] = df['close'].shift(i)
    df.dropna(inplace=True)
    return df

data = create_features(data)

# 分割特徵和目標
X = data.drop('close', axis=1)
y = data['close']

# 分割訓練測試集（時間序列，不要 shuffle）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# 訓練線性回歸模型（簡單 AI 模型）
model = LinearRegression()
model.fit(X_train, y_train)

# 預測
predictions = model.predict(X_test)

# 計算 MSE
mse = mean_squared_error(y_test, predictions)
print(f"Mean Squared Error: {mse}")

# 模擬交易：基於預測決定買賣
# 簡單策略：如果預測 > 當前價格，買入；否則賣出
# 使用測試數據模擬
initial_balance = 10000
balance = initial_balance
position = 0  # 持股數

results = []
actual_prices = y_test.values
pred_prices = predictions
test_dates = y_test.index

for i in range(1, len(pred_prices)):  # 從 1 開始，因為需要前一天價格
    current_price = actual_prices[i-1]  # 前一天作為"當前"價格
    predicted = pred_prices[i]  # 預測下一天
    
    if predicted > current_price and position == 0:
        # 買入
        shares_to_buy = balance // current_price
        if shares_to_buy > 0:
            position = shares_to_buy
            balance -= position * current_price
            results.append(f"{test_dates[i]}: Buy {position} shares at {current_price:.2f}, balance: {balance:.2f}")
    
    elif predicted < current_price and position > 0:
        # 賣出
        balance += position * current_price
        results.append(f"{test_dates[i]}: Sell {position} shares at {current_price:.2f}, balance: {balance:.2f}")
        position = 0

# 最後如果有持股，賣出
if position > 0:
    last_price = actual_prices[-1]
    balance += position * last_price
    results.append(f"{test_dates[-1]}: Final sell {position} shares at {last_price:.2f}, balance: {balance:.2f}")

final_balance = balance
profit = final_balance - initial_balance
print(f"Initial Balance: {initial_balance}")
print(f"Final Balance: {final_balance:.2f}")
print(f"Profit: {profit:.2f}")
print("\nTrading Actions:")
for action in results:
    print(action)