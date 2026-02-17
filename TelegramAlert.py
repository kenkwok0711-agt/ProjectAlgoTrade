import ccxt
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()

# ================== 配置區 ==================
SYMBOL = 'BTC/USDT'          # 可改 ETH/USDT, SOL/USDT 等
CHECK_INTERVAL = 10          # 秒，監控頻率（別太頻繁，避免 API 限速）
BASIS_THRESHOLD = 0.30       # %，超過絕對值才通知（可調 0.2~0.5）
MIN_FUNDING_ABS = 0.01       # %，Funding Rate 絕對值太小可忽略
USE_TESTNET = True           # 先用 True 測試！
DRY_RUN = True               # True = 只監控 + 通知，不真實下單

# Telegram 配置
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')  # 必須是 str 或 int
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("缺少 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID，請檢查 .env")

telegram_bot = Bot(token=TELEGRAM_TOKEN)

# Binance 現貨 & 永續
spot = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True,
})

futures = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret': os.getenv('BINANCE_API_SECRET'),
    'enableRateLimit': True,
    'options': {'defaultType': 'future'},
})

if USE_TESTNET:
    spot.set_sandbox_mode(True)
    futures.set_sandbox_mode(True)
    print("🔧 使用 Binance Testnet")

print("🚀 期現套利監控 + Telegram 通知 已啟動...")

async def send_telegram(message):
    """非同步發送 Telegram 訊息"""
    try:
        await telegram_bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        print(f"Telegram 已發送: {message}")
    except TelegramError as e:
        print(f"Telegram 發送失敗: {e}")

# ================== 主循環 ==================
while True:
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. 取價格
        spot_ticker = spot.fetch_ticker(SYMBOL)
        spot_price = spot_ticker['last']

        fut_ticker = futures.fetch_ticker(SYMBOL)
        fut_price = fut_ticker['last']

        funding_info = futures.fetch_funding_rate(SYMBOL)
        funding_rate = funding_info['fundingRate'] * 100  # %

        basis = (fut_price - spot_price) / spot_price * 100

        status_line = (
            f"[{now}] {SYMBOL}\n"
            f"現貨: {spot_price:,.2f} USDT\n"
            f"永續: {fut_price:,.2f} USDT\n"
            f"Basis: {basis:+.4f}%\n"
            f"Funding Rate: {funding_rate:+.4f}%"
        )

        print(status_line)

        # 2. 機會判斷 & 通知
        alert_message = None

        if basis > BASIS_THRESHOLD and funding_rate > MIN_FUNDING_ABS:
            alert_message = (
                f"🔥 *正向套利機會！*\n"
                f"{status_line}\n"
                f"建議：買現貨 + 賣空永續（可收 Funding）\n"
                f"Basis 超過 {BASIS_THRESHOLD}% 閾值"
            )
            if not DRY_RUN:
                # 可在此加下單邏輯（小心！）
                print("   → 模擬執行正向套利")

        elif basis < -BASIS_THRESHOLD and funding_rate < -MIN_FUNDING_ABS:
            alert_message = (
                f"🔥 *反向套利機會！*\n"
                f"{status_line}\n"
                f"建議：買永續 + 賣空現貨（或借幣）\n"
                f"Basis 低於 {-BASIS_THRESHOLD}%"
            )
            if not DRY_RUN:
                print("   → 模擬執行反向套利")

        if alert_message:
            # 因為 send_message 是 async，需要 asyncio
            import asyncio
            asyncio.run(send_telegram(alert_message))

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        error_msg = f"❌ 錯誤發生: {str(e)}"
        print(error_msg)
        asyncio.run(send_telegram(error_msg))  # 也通知錯誤
        time.sleep(30)  # 錯誤後等久一點