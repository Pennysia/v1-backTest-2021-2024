# External data sources
import yfinance as yf
import requests  # still imported for potential future use / demonstration
import pandas as pd
from datetime import datetime, timedelta
import time

# Define coins and their CoinGecko IDs
coins = {
    # symbol: Yahoo Finance ticker (vs USD)
    'BTC': 'BTC-USD',
    'ETH': 'ETH-USD',
    'DOT': 'DOT-USD',
    'CRV': 'CRV-USD',
    'GALA': 'GALA-USD',
    'USDC': 'USDC-USD',
    'USDT': 'USDT-USD',
    'LINK': 'LINK-USD'
}

# Date range
start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 12, 31)

# Prepare DataFrame to collect data
dates = pd.date_range(start_date, end_date, freq='D')
df = pd.DataFrame({'Date': dates})
df.set_index('Date', inplace=True)

# Function to fetch historical prices via Yahoo Finance
def fetch_history(ticker: str) -> pd.Series:
    """Return daily close prices using yfinance (no API keys required)."""

    # yfinance uses inclusive-exclusive for end date, so add one day
    _end = end_date + timedelta(days=1)
    data = yf.download(ticker, start=start_date.date(), end=_end.date(), interval="1d", progress=False)

    if data.empty:
        print(f"Warning: no data returned for {ticker} via yfinance.")
        return pd.Series(dtype=float)

    series = data['Close']
    series.index = pd.to_datetime(series.index)
    return series

# Fetch for each coin
for symbol, yf_ticker in coins.items():
    print(f"Fetching {symbol} ({yf_ticker}) ...")
    df[symbol] = fetch_history(yf_ticker)

# Save to CSV
output_path = '../data/crypto_prices_2021_2024.csv'
df.to_csv(output_path, float_format='%.6f')
print(f"\nSaved CSV to: {output_path}")