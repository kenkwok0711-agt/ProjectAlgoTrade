import ccxt
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ================== 配置區 ==================
SYMBOL = 'BTC/USDT'          # 可改成 ETH/USDT 等
CHECK_INTERVAL = 5           # 秒，監控頻率
BASIS_THRESHOLD = 0.25       # %，超過此值才提示機會（可調整）
TRADE_AMOUNT_BTC = 0.001     # 單次交易數量（測試時用小額）
USE_TESTNET = True           # 強烈建議先開 True，用測試網
DRY_RUN = True               # True = 只模擬，不真實下單（安全！）

# API 金鑰（建議用 .env 存放，絕對不要 commit 到 GitHub）
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

# ================== 初始化交易所 ==================
# 現貨
spot = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
})

# 永續合約
futures = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future',   # 關鍵：切換到永續合約
    },
})

if USE_TESTNET:
    spot.set_sandbox_mode(True)
    futures.set_sandbox_mode(True)
    print("🔧 已切換到 Binance Testnet（測試網）")

print("🚀 期現套利監控程式啟動...")

# ================== 主循環 ==================
while True:
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. 取得現貨價格
        spot_ticker = spot.fetch_ticker(SYMBOL)
        spot_price = spot_ticker['last']

        # 2. 取得永續合約價格 + 資金費率
        fut_ticker = futures.fetch_ticker(SYMBOL)
        fut_price = fut_ticker['last']
        funding = futures.fetch_funding_rate(SYMBOL)
        funding_rate = funding['fundingRate'] * 100  # 轉成百分比

        basis = (fut_price - spot_price) / spot_price * 100

        print(f"\n[{now}] {SYMBOL}")
        print(f"  現貨價格 : {spot_price:,.2f} USDT")
        print(f"  永續價格 : {fut_price:,.2f} USDT")
        print(f"  Basis    : {basis:+.4f}%")
        print(f"  Funding  : {funding_rate:+.4f}% (下一結算)")

        # 3. 機會判斷
        if basis > BASIS_THRESHOLD:
            print("✅ 正向套利機會！建議：買現貨 + 賣空永續")
            if not DRY_RUN:
                # 實際執行（測試時請務必先用小額 + Testnet）
                spot.create_market_buy_order(SYMBOL, TRADE_AMOUNT_BTC)
                futures.create_market_sell_order(SYMBOL, TRADE_AMOUNT_BTC)
                print("   → 已執行買現貨 + 賣空永續")

        elif basis < -BASIS_THRESHOLD:
            print("✅ 反向套利機會！建議：賣空現貨 + 買多永續")
            # 反向執行代碼可自行補上（需處理賣空現貨或借幣）

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print(f"❌ 錯誤: {e}")
        time.sleep(10)