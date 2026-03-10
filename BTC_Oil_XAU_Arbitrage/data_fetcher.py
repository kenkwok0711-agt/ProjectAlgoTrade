# data_fetcher.py
# Module to fetch real-time and historical price data using Polygon and CoinGecko.

from datetime import datetime, timedelta
from polygon import RESTClient  # Assuming polygon is available
from pycoingecko import CoinGeckoAPI  # Assuming coingecko is available

# Polygon API key (configured in env, but placeholder)
POLYGON_KEY = 'YOUR_POLYGON_API_KEY'  # Replace if needed

polygon_client = RESTClient(POLYGON_KEY)
cg = CoinGeckoAPI()

def fetch_prices(assets):
    prices = {}
    for asset in assets:
        if asset == 'BTC':
            # Fetch BTC from CoinGecko
            data = cg.get_price(ids='bitcoin', vs_currencies='usd')
            prices['BTC'] = data['bitcoin']['usd']
        else:
            # Fetch futures from Polygon (e.g., CL for Crude, GC for Gold, SI for Silver)
            # Note: Polygon uses tickers like 'CL' for crude oil futures
            # This assumes continuous contract; adjust for specific expiry
            ticker = f'X:{asset}'  # Polygon format for commodities/futures
            quote = polygon_client.get_last_quote(ticker)
            prices[asset] = (quote.ask + quote.bid) / 2  # Mid price
    return prices

def fetch_historical_data(asset, days):
    historical = []
    end = datetime.now()
    start = end - timedelta(days=days)
    
    if asset == 'BTC':
        # CoinGecko historical (daily)
        data = cg.get_coin_market_chart_range_by_id(id='bitcoin', vs_currency='usd', 
                                                    from_timestamp=start.timestamp(), 
                                                    to_timestamp=end.timestamp())
        historical = data['prices']  # List of [timestamp, price]
    else:
        # Polygon historical bars
        ticker = f'X:{asset}'
        bars = polygon_client.get_aggs(ticker=ticker, multiplier=1, timespan='day', 
                                       from_=start.date(), to=end.date())
        historical = [[bar.timestamp, bar.close] for bar in bars]
    
    # Return only closing prices
    return [price for ts, price in historical]