# trade_executor.py
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY, SELL
from config import HOST, CHAIN_ID, PRIVATE_KEY, FUNDER, SIGNATURE_TYPE, COPY_AMOUNT_USD
import time

client = None

def init_client():
    global client
    client = ClobClient(
        HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=SIGNATURE_TYPE,
        funder=FUNDER
    )
    client.set_api_creds(client.create_or_derive_api_creds())
    print("✅ Polymarket 客戶端初始化完成")

def execute_copy_trade(signal: dict):
    global client
    if not client:
        init_client()
    
    side = BUY if signal["side"] == "BUY" else SELL
    token_id = signal["token_id"]
    
    # 抓市場參數
    market_info = get_market_details(token_id)  # 從 data_fetcher 匯入
    if not market_info:
        print("⚠️ 無法取得市場資訊，跳過")
        return
    
    mo = MarketOrderArgs(
        token_id=token_id,
        amount=COPY_AMOUNT_USD,      # 跟單金額
        side=side,
        order_type=OrderType.FOK     # Fill-Or-Kill
    )
    
    try:
        signed = client.create_market_order(mo)
        resp = client.post_order(signed, OrderType.FOK)
        print(f"✅ 成功跟單！ token={token_id} side={signal['side']} 金額=${COPY_AMOUNT_USD}")
        print(resp)
    except Exception as e:
        print(f"❌ 跟單失敗: {e}")