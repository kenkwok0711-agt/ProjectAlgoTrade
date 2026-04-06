import sqlite3
from datetime import datetime
from config import DB_PATH

def update_wallet_score(wallet: str, trades: list):
    """簡單勝率 + ROI 計算（可後續改成呼叫 PNL subgraph 更精準）"""
    if not trades:
        return
    
    wins = sum(1 for t in trades if t.get('profit') and t['profit'] > 0)  # 實際上可從已結算市場計算
    total = len(trades)
    win_rate = wins / total if total else 0.0
    # 簡化 ROI（實際應計算已實現損益）
    roi = 0.15  # 占位，後續可替換成 subgraph 查詢
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO wallet_scores 
                 VALUES (?,?,?,?,?)''',
              (wallet, win_rate, roi, total, int(datetime.now().timestamp())))
    conn.commit()
    conn.close()
    print(f"✅ {wallet[:8]}... 分數更新: 勝率 {win_rate:.1%}")