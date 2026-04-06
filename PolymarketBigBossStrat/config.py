import os
from dotenv import load_dotenv

load_dotenv()

# Polymarket CLOB
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon

PRIVATE_KEY = os.getenv("PRIVATE_KEY")          # 你的錢包私鑰
FUNDER = os.getenv("FUNDER")                    # 你的錢包地址（EOA）
SIGNATURE_TYPE = 0                              # 0 = EOA（最簡單）

# Data API（查任意錢包交易）
DATA_API_BASE = "https://data-api.polymarket.com/activity"

# 錢包清單（建議先放 200~500 個）
WALLETS_JSON = "wallets.json"

# 信號門檻
MIN_WALLETS_FOR_SIGNAL = 3          # 至少幾個大戶同時押同一邊
TIME_WINDOW_SECONDS = 300           # 5 分鐘內

# 跟單大小（每筆跟單金額，美元）
COPY_AMOUNT_USD = 50.0

# 資料庫
DB_PATH = "wallet_hunter.db"

# 輪詢間隔（秒）
POLL_INTERVAL = 30