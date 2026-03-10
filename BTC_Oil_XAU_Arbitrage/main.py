# main.py
# This is the main script that runs the trading arbitrage loop.
# It monitors BTC, Crude Oil Futures (CL), Gold (GC), and Silver (SI).
# Requires API keys for Polygon.io, CoinGecko (configured in env), and Telegram Bot.

import time
import logging
from data_fetcher import fetch_prices, fetch_historical_data
from strategy import calculate_rsi, get_bargain_index, should_sell, select_best_to_buy
from alert import send_telegram_alert

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Assets to monitor
ASSETS = ['BTC', 'CL', 'GC', 'SI']  # BTC (crypto), CL (Crude Oil Futures), GC (Gold Futures), SI (Silver Futures)

# Strategy parameters
PROFIT_THRESHOLD = 0.30  # 30% profit to sell
RSI_PERIOD = 14  # Standard RSI period
OVERSOLD_THRESHOLD = 30  # RSI < 30 considered oversold for bargain index

# Portfolio state (simulated for demo; in real, integrate with exchange API)
portfolio = {asset: {'holding': False, 'buy_price': None} for asset in ASSETS}

# Telegram bot token and chat ID (replace with your own)
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

def main():
    logging.info("Starting trading arbitrage loop...")
    current_holdings = None  # Track current holding asset

    while True:
        try:
            # Fetch current prices
            prices = fetch_prices(ASSETS)
            logging.info(f"Current prices: {prices}")

            # Check if we need to sell current holding
            if current_holdings:
                asset = current_holdings
                if portfolio[asset]['holding']:
                    current_price = prices[asset]
                    buy_price = portfolio[asset]['buy_price']
                    if should_sell(current_price, buy_price, PROFIT_THRESHOLD):
                        logging.info(f"Selling {asset} at {current_price} (bought at {buy_price})")
                        # Simulate sell (in real, call exchange API)
                        portfolio[asset]['holding'] = False
                        portfolio[asset]['buy_price'] = None
                        current_holdings = None

            # If no holding, select and buy the best bargain
            if not current_holdings:
                # Fetch historical data for RSI calculation
                historical_data = {asset: fetch_historical_data(asset, RSI_PERIOD + 1) for asset in ASSETS}
                
                # Calculate RSI for each
                rsis = {asset: calculate_rsi(historical_data[asset], RSI_PERIOD) for asset in ASSETS}
                
                # Get bargain indices (lower RSI = better bargain if oversold)
                bargain_indices = {asset: get_bargain_index(rsis[asset], OVERSOLD_THRESHOLD) for asset in ASSETS}
                
                # Select the best to buy
                best_asset = select_best_to_buy(bargain_indices)
                if best_asset:
                    buy_price = prices[best_asset]
                    logging.info(f"Buying {best_asset} at {buy_price}")
                    # Simulate buy (in real, call exchange API)
                    portfolio[best_asset]['holding'] = True
                    portfolio[best_asset]['buy_price'] = buy_price
                    current_holdings = best_asset
                    
                    # Send Telegram alert
                    message = f"Successfully bought {best_asset} at {buy_price}"
                    send_telegram_alert(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, message)

            # Sleep for a monitoring interval (e.g., 1 minute)
            time.sleep(60)

        except Exception as e:
            logging.error(f"Error in loop: {e}")
            time.sleep(60)  # Retry after error

if __name__ == "__main__":
    main()