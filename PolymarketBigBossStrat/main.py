import time
import json
from config import POLL_INTERVAL, WALLETS_JSON
from database import init_db
from data_fetcher import load_wallets, fetch_wallet_activity, get_market_details
from database import save_trade
from wallet_scorer import update_wallet_score
from signal_detector import detect_signals
from trade_executor import init_client, execute_copy_trade

if __name__ == "__main__":
    init_db()
    init_client()
    
    print("🚀 錢包獵手啟動！掃描中...")
    wallets = load_wallets()   # 你的 14000 個錢包清單
    
    while True:
        for wallet in wallets[:500]:   # 先跑前 500 個，防止 rate limit
            try:
                activities = fetch_wallet_activity(wallet, limit=20)
                for act in activities:
                    if act.get('type') == 'TRADE':
                        trade = {
                            'id': act['id'],
                            'wallet': wallet,
                            'token_id': act['tokenId'],
                            'side': act['side'],          # BUY / SELL
                            'price': float(act['price']),
                            'size': float(act['size']),
                            'timestamp': int(act['timestamp']),
                            'market_slug': act.get('marketSlug', '')
                        }
                        save_trade(trade)
                        # 簡單更新分數（可改成定期批量更新）
                        update_wallet_score(wallet, [trade])
            except Exception as e:
                continue  # 單一錢包錯誤不中斷
        
        # 偵測信號
        signal = detect_signals()
        if signal:
            execute_copy_trade(signal)
        
        print(f"[{time.strftime('%H:%M:%S')}] 掃描完成，休息 {POLL_INTERVAL} 秒...")
        time.sleep(POLL_INTERVAL)