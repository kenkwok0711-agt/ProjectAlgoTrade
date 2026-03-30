# main.py
# 這是整個交易套利策略的主程式

import time                                                # 引入時間模組，用來控制迴圈間隔
import logging                                             # 引入 logging 模組，用來記錄程式執行資訊
from data_fetcher import fetch_prices, fetch_historical_data   # 從 data_fetcher 模組引入價格取得函式
from strategy import calculate_rsi, get_bargain_index, should_sell, select_best_to_buy   # 從 strategy 模組引入交易策略相關函式
from alert import send_telegram_alert                      # 從 alert 模組引入 Telegram 通知函式

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')   # 設定 logging 等級為 INFO，並定義輸出格式

ASSETS = ['BTC', 'CL', 'GC', 'SI']                         # 要監控的資產清單：比特幣、原油期貨、黃金期貨、白銀期貨

PROFIT_THRESHOLD = 0.30                                    # 賣出獲利門檻：獲利 30% 以上就賣出
RSI_PERIOD = 14                                            # RSI 計算週期，標準設定為 14
OVERSOLD_THRESHOLD = 30                                    # RSI 超賣門檻，低於 30 視為超賣

portfolio = {asset: {'holding': False, 'buy_price': None} for asset in ASSETS}   # 模擬投資組合狀態，每個資產記錄是否持有及買入價格

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'                 # Telegram 機器人 Token（請替換成你自己的）
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'                          # Telegram 通知的聊天室 ID（請替換成你自己的）

def main():                                                # 主程式函式
    logging.info("Starting trading arbitrage loop...")     # 記錄程式開始執行
    current_holdings = None                                # 用來追蹤目前持有的資產，初始為 None

    while True:                                            # 進入無限迴圈，持續監控市場
        try:                                               # 開始例外處理區塊
            prices = fetch_prices(ASSETS)                  # 取得所有監控資產的即時價格
            logging.info(f"Current prices: {prices}")      # 記錄目前取得的價格資訊

            # 檢查是否需要賣出目前持倉
            if current_holdings:                           # 如果目前有持倉
                asset = current_holdings                   # 取得目前持有的資產代碼
                if portfolio[asset]['holding']:            # 確認該資產確實處於持有狀態
                    current_price = prices[asset]          # 取得該資產的當前價格
                    buy_price = portfolio[asset]['buy_price']   # 取得當初買入的價格
                    if should_sell(current_price, buy_price, PROFIT_THRESHOLD):   # 判斷是否應該賣出
                        logging.info(f"Selling {asset} at {current_price} (bought at {buy_price})")   # 記錄賣出資訊
                        portfolio[asset]['holding'] = False   # 更新投資組合狀態為未持有
                        portfolio[asset]['buy_price'] = None   # 清空買入價格
                        current_holdings = None                # 清空目前持倉記錄

            # 如果目前沒有持倉，才考慮買入
            if not current_holdings:                       # 如果目前沒有持倉，才考慮買入
                historical_data = {asset: fetch_historical_data(asset, RSI_PERIOD + 1) for asset in ASSETS}   # 取得每個資產的歷史價格資料，用來計算 RSI

                rsis = {asset: calculate_rsi(historical_data[asset], RSI_PERIOD) for asset in ASSETS}   # 為每個資產計算 RSI 值

                bargain_indices = {asset: get_bargain_index(rsis[asset], OVERSOLD_THRESHOLD) for asset in ASSETS}   # 根據 RSI 計算每個資產的便宜指數

                best_asset = select_best_to_buy(bargain_indices)   # 選擇目前最值得買入的資產
                if best_asset:                                     # 如果有找到適合買入的資產
                    buy_price = prices[best_asset]                 # 取得該資產的買入價格
                    logging.info(f"Buying {best_asset} at {buy_price}")   # 記錄買入資訊
                    portfolio[best_asset]['holding'] = True        # 更新投資組合為持有狀態
                    portfolio[best_asset]['buy_price'] = buy_price # 記錄買入價格
                    current_holdings = best_asset                  # 更新目前持倉資產

                    message = f"Successfully bought {best_asset} at {buy_price}"   # 準備 Telegram 通知訊息
                    send_telegram_alert(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, message)   # 發送買入通知到 Telegram

            time.sleep(60)                                         # 每次迴圈結束後休息 60 秒（1 分鐘）

        except Exception as e:                                     # 捕捉任何執行過程中的錯誤
            logging.error(f"Error in loop: {e}")                   # 記錄錯誤訊息
            time.sleep(60)                                         # 發生錯誤後也休息 60 秒再重試

if __name__ == "__main__":                                         # 程式進入點
    main()                                                         # 呼叫主程式函式開始執行