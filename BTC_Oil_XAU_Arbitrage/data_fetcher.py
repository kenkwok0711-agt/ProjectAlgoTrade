# data_fetcher.py
# 模組：用來取得即時價格與歷史價格資料，支援 Polygon 與 CoinGecko

from datetime import datetime, timedelta                    # 引入日期與時間處理相關模組
from polygon import RESTClient                              # 引入 Polygon 的 REST API 客戶端
from pycoingecko import CoinGeckoAPI                        # 引入 CoinGecko 的 Python API 套件

# Polygon API 金鑰（建議設定在環境變數中，這裡只是範例）
POLYGON_KEY = 'YOUR_POLYGON_API_KEY'                        # 請替換成你自己的 Polygon API 金鑰

polygon_client = RESTClient(POLYGON_KEY)                    # 建立 Polygon RESTClient 實例
cg = CoinGeckoAPI()                                         # 建立 CoinGeckoAPI 實例

def fetch_prices(assets):                                   # 定義函式：取得多個資產的即時價格
    prices = {}                                             # 建立空字典，用來儲存各資產的價格
    for asset in assets:                                    # 逐一處理傳入的資產清單
        if asset == 'BTC':                                  # 如果資產是比特幣
            # Fetch BTC from CoinGecko
            data = cg.get_price(ids='bitcoin', vs_currencies='usd')   # 從 CoinGecko 取得比特幣即時價格（單位：美元）
            prices['BTC'] = data['bitcoin']['usd']          # 將比特幣價格存入字典
        else:                                               # 其他資產（如原油、黃金、白銀期貨）
            # Fetch futures from Polygon (e.g., CL for Crude, GC for Gold, SI for Silver)
            # Note: Polygon uses tickers like 'CL' for crude oil futures
            ticker = f'X:{asset}'                           # 將資產代碼轉換成 Polygon 期貨格式（例如 X:CL）
            quote = polygon_client.get_last_quote(ticker)   # 從 Polygon 取得該期貨的最新報價
            prices[asset] = (quote.ask + quote.bid) / 2     # 計算買賣價中間值（Mid Price）作為當前價格
    return prices                                           # 回傳包含所有資產即時價格的字典

def fetch_historical_data(asset, days):                     # 定義函式：取得單一資產的歷史價格資料
    historical = []                                         # 建立空列表，用來儲存歷史價格
    end = datetime.now()                                    # 取得當前日期時間
    start = end - timedelta(days=days)                      # 計算起始日期（今天往前推指定天數）
    
    if asset == 'BTC':                                      # 如果資產是比特幣
        # CoinGecko historical (daily)
        data = cg.get_coin_market_chart_range_by_id(        # 從 CoinGecko 取得比特幣歷史價格範圍資料
            id='bitcoin', 
            vs_currency='usd', 
            from_timestamp=start.timestamp(), 
            to_timestamp=end.timestamp()
        )
        historical = data['prices']                         # CoinGecko 回傳的是 [時間戳, 價格] 的列表
    else:                                                   # 其他資產使用 Polygon 取得歷史資料
        # Polygon historical bars
        ticker = f'X:{asset}'                               # 設定 Polygon 期貨 ticker 格式
        bars = polygon_client.get_aggs(                     # 從 Polygon 取得每日 K 線資料
            ticker=ticker, 
            multiplier=1, 
            timespan='day', 
            from_=start.date(), 
            to=end.date()
        )
        historical = [[bar.timestamp, bar.close] for bar in bars]   # 提取每根 K 線的時間戳與收盤價
    
    # Return only closing prices
    return [price for ts, price in historical]              # 只回傳收盤價列表（去除時間戳）