import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import datetime

# 生成合成股票數據（模擬 AAPL 收盤價）
np.random.seed(42)                                      # 設定隨機種子，確保每次執行結果一致
dates = pd.date_range(start='2023-01-01', periods=365, freq='D')   # 建立從 2023-01-01 開始，共 365 天的日期序列
prices = np.cumsum(np.random.randn(365) * 2 + 0.1) + 150   # 模擬隨機遊走價格，從 150 元開始，每天有隨機波動
data = pd.DataFrame({'close': prices}, index=dates)         # 將價格轉換為 DataFrame，並以日期作為索引

# 創建特徵：使用前幾天的收盤價預測下一天
def create_features(df, lag=5):
    for i in range(1, lag+1):                               # 迴圈建立過去 1 到 5 天的滯後特徵
        df[f'lag_{i}'] = df['close'].shift(i)               # 建立 lag_i 欄位，代表 i 天前的收盤價
    df.dropna(inplace=True)                                 # 刪除因為 shift 產生的 NaN 值
    return df

data = create_features(data)                                # 對數據套用特徵工程，加入滯後特徵

# 分割特徵和目標
X = data.drop('close', axis=1)                              # 特徵 X：移除目標變數 close，只保留 lag 特徵
y = data['close']                                           # 目標變數 y：當天的收盤價（要預測的目標）

# 分割訓練測試集（時間序列，不要 shuffle）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)  
                                                            # 按時間順序分割資料，前 80% 為訓練集，後 20% 為測試集

# 訓練線性回歸模型（簡單 AI 模型）
model = LinearRegression()                                  # 建立線性回歸模型物件
model.fit(X_train, y_train)                                 # 使用訓練資料訓練模型

# 預測
predictions = model.predict(X_test)                         # 對測試集進行價格預測

# 計算 MSE
mse = mean_squared_error(y_test, predictions)               # 計算均方誤差（Mean Squared Error）
print(f"Mean Squared Error: {mse}")                         # 輸出模型的 MSE 評估結果

# 模擬交易：基於預測決定買賣
# 簡單策略：如果預測 > 當前價格，買入；否則賣出
# 使用測試數據模擬
initial_balance = 10000                                     # 設定初始資金為 10000 元
balance = initial_balance                                   # 目前帳戶餘額
position = 0                                                # 目前持有的股票數量（0 表示空倉）

results = []                                                # 用來記錄所有交易動作的列表
actual_prices = y_test.values                               # 測試集的實際收盤價（陣列形式）
pred_prices = predictions                                   # 模型預測的收盤價
test_dates = y_test.index                                   # 測試集的日期索引

for i in range(1, len(pred_prices)):                        # 從第 1 筆開始迴圈（因為需要用到前一天價格）
    current_price = actual_prices[i-1]                      # 前一天的實際價格，視為「當前價格」
    predicted = pred_prices[i]                              # 模型預測的「下一天」價格
    
    if predicted > current_price and position == 0:         # 如果預測上漲且目前沒有持股 → 買入
        # 買入
        shares_to_buy = balance // current_price            # 計算可以用全部資金買進多少股（整數）
        if shares_to_buy > 0:                               # 如果有足夠資金買入
            position = shares_to_buy                        # 更新持股數量
            balance -= position * current_price             # 扣除買入花費的金額
            results.append(f"{test_dates[i]}: Buy {position} shares at {current_price:.2f}, balance: {balance:.2f}")
                                                            # 記錄買入動作
    
    elif predicted < current_price and position > 0:        # 如果預測下跌且目前有持股 → 賣出
        # 賣出
        balance += position * current_price                 # 賣出後增加帳戶餘額
        results.append(f"{test_dates[i]}: Sell {position} shares at {current_price:.2f}, balance: {balance:.2f}")
                                                            # 記錄賣出動作
        position = 0                                        # 清空持股

# 最後如果有持股，強制在最後一天賣出
if position > 0:
    last_price = actual_prices[-1]                          # 取得最後一天的實際價格
    balance += position * last_price                        # 賣出所有持股
    results.append(f"{test_dates[-1]}: Final sell {position} shares at {last_price:.2f}, balance: {balance:.2f}")
                                                            # 記錄最終賣出動作

final_balance = balance                                     # 最終帳戶餘額
profit = final_balance - initial_balance                    # 計算總獲利
print(f"Initial Balance: {initial_balance}")                # 輸出初始資金
print(f"Final Balance: {final_balance:.2f}")                # 輸出最終資金
print(f"Profit: {profit:.2f}")                              # 輸出總獲利金額
print("\nTrading Actions:")                                 # 標題：交易紀錄
for action in results:                                      # 逐行印出所有交易動作
    print(action)
