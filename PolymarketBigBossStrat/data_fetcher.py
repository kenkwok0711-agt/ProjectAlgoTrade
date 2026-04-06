import requests
import json
from config import DATA_API_BASE, WALLETS_JSON

def load_wallets():
    with open(WALLETS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)  # list of addresses

def fetch_wallet_activity(wallet: str, limit: int = 50):
    """用官方 Data API 抓單一錢包最近交易"""
    params = {
        "user": wallet.lower(),
        "type": "TRADE",
        "limit": limit,
        "sortBy": "TIMESTAMP",
        "sortDirection": "DESC"
    }
    resp = requests.get(DATA_API_BASE, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()  # 回傳 list of activity

def get_market_details(token_id: str):
    """從 gamma-api 拿市場資訊（tick size, neg_risk）"""
    resp = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={"clobTokenIds": token_id},
        timeout=10
    )
    data = resp.json()
    if data:
        market = data[0]
        return {
            "tick_size": market["minimumTickSize"],
            "neg_risk": market["negRisk"],
            "slug": market.get("slug", "")
        }
    return None