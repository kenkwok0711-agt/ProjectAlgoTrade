import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 交易紀錄
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
        id TEXT PRIMARY KEY,
        wallet TEXT,
        token_id TEXT,
        side TEXT,           -- BUY / SELL
        price REAL,
        size REAL,
        timestamp INTEGER,
        market_slug TEXT
    )''')
    
    # 錢包分數（定期更新）
    c.execute('''CREATE TABLE IF NOT EXISTS wallet_scores (
        wallet TEXT PRIMARY KEY,
        win_rate REAL,
        roi REAL,
        total_trades INTEGER,
        last_updated INTEGER
    )''')
    
    conn.commit()
    conn.close()

def save_trade(trade):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO trades 
                 VALUES (?,?,?,?,?,?,?,?)''',
              (trade['id'], trade['wallet'], trade['token_id'],
               trade['side'], trade['price'], trade['size'],
               trade['timestamp'], trade.get('market_slug', '')))
    conn.commit()
    conn.close()

def get_recent_trades(minutes: int = 10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cutoff = int(datetime.now().timestamp()) - minutes * 60
    c.execute("SELECT * FROM trades WHERE timestamp >= ?", (cutoff,))
    rows = c.fetchall()
    conn.close()
    return rows