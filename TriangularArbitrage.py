# 極簡三角套利檢查：BTC/USD * USDT/BTC * USDT/USD - 1 > 0
# 只檢查價格，不下單、不記錄、不處理深度
# 執行環境需已 pip install ccxt

import ccxt
import time

# 你可以改成其他交易所組合，例如 binance + bybit + okx
ex1 = ccxt.binance()          # BTC/USD 或 BTC/USDT
ex2 = ccxt.okx()              # USDT/BTC
ex3 = ccxt.bybit()            # USDT/USD (穩定幣對)

# 有些交易所用 BTC/USDT 而非 BTC/USD，這裡用 USDT 對統一處理
SYMBOL_BTC_USDT  = 'BTC/USDT'   # ex1
SYMBOL_USDT_BTC  = 'USDT/BTC'   # ex2 (反向)
SYMBOL_USDT_USD  = 'USDT/USD'   # ex3 (或 USDT/USDC)

def get_price(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print(f"[{exchange.id}] 取 {symbol} 價格失敗：{e}")
        return None

print("開始監控三角套利機會 (BTC/USDT → USDT/BTC → USDT/USD)")
print("條件： (BTC/USDT) * (USDT/BTC) * (USDT/USD) - 1 > 0\n")

while True:
    p1 = get_price(ex1, SYMBOL_BTC_USDT)     # BTC/USDT
    p2 = get_price(ex2, SYMBOL_USDT_BTC)     # USDT/BTC (通常很小)
    p3 = get_price(ex3, SYMBOL_USDT_USD)     # USDT/USD ≈ 1

    if None in (p1, p2, p3):
        print("─ 資料不完整，等待下一次 ─")
    else:
        product = p1 * p2 * p3
        diff = product - 1
        diff_pct = diff * 100

        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}", end="  ")
        print(f"BTC/USDT = {p1:,.2f}   USDT/BTC = {p2:,.8f}   USDT/USD = {p3:,.4f}")
        print(f"乘積 = {product:.8f}    價差 = {diff:.8f} ({diff_pct:+.4f}%)")

        if diff > 0:
            print("!!! 發現正向套利機會 !!!")
            print(f"預估收益率：{diff_pct:.4f}% (未扣手續費)\n")
        elif diff < -0.0005:  # 小於 -0.05% 才提示反向，避免雜訊
            print(f"反向機會：{ -diff_pct :.4f}% (可考慮反方向)\n")
        else:
            print("無明顯機會\n")

    time.sleep(5)  # 每 5 秒檢查一次，可自行調整