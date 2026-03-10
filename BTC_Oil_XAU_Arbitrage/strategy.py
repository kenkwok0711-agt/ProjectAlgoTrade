# strategy.py
# Module for strategy logic: RSI calculation, bargain index, sell/buy decisions.

import numpy as np

def calculate_rsi(prices, period=14):
    """
    Calculate RSI manually using numpy.
    prices: list of closing prices, length > period
    """
    if len(prices) <= period:
        return 50  # Neutral if insufficient data
    
    deltas = np.diff(prices)
    gains = deltas.copy()
    losses = deltas.copy()
    gains[gains < 0] = 0
    losses[losses > 0] = 0
    losses = abs(losses)
    
    avg_gain = gains[:period].mean()
    avg_loss = losses[:period].mean()
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # For remaining
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
    
    return rsi

def get_bargain_index(rsi, oversold_threshold=30):
    """
    Bargain index: Similar to oversold RSI. Lower RSI (if < threshold) means better bargain.
    If RSI >= threshold, index = infinity (not bargain).
    Else, index = RSI (lower is better)
    """
    if rsi < oversold_threshold:
        return rsi
    return float('inf')

def should_sell(current_price, buy_price, threshold=0.30):
    """
    Check if profit exceeds threshold.
    """
    if buy_price is None:
        return False
    profit = (current_price - buy_price) / buy_price
    return profit >= threshold

def select_best_to_buy(bargain_indices):
    """
    Select asset with lowest bargain index (best bargain).
    If all inf, return None (no bargain available).
    """
    min_index = min(bargain_indices.values())
    if min_index == float('inf'):
        return None
    for asset, index in bargain_indices.items():
        if index == min_index:
            return asset
    return None