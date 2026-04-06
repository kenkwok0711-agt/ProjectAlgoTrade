from collections import defaultdict
from datetime import datetime
from config import MIN_WALLETS_FOR_SIGNAL, TIME_WINDOW_SECONDS
from database import get_recent_trades

def detect_signals():
    recent = get_recent_trades(minutes=TIME_WINDOW_SECONDS//60 + 2)
    if not recent:
        return None
    
    # key = (token_id, side)
    groups = defaultdict(list)
    for row in recent:
        _, wallet, token_id, side, price, size, ts, slug = row
        key = (token_id, side)
        groups[key].append((wallet, ts, price, size, slug))
    
    for key, trades in groups.items():
        unique_wallets = len(set(w[0] for w in trades))
        if unique_wallets >= MIN_WALLETS_FOR_SIGNAL:
            latest_ts = max(w[1] for w in trades)
            print(f"🚨 強烈信號！{unique_wallets} 個大戶在 {key[0]} 同時 {key[1]}")
            return {
                "token_id": key[0],
                "side": key[1],           # BUY / SELL
                "confidence": unique_wallets / 5.0,  # 簡單置信度
                "timestamp": latest_ts,
                "market_slug": trades[0][4]
            }
    return None