import requests
import pandas as pd
import time

def fetch_kraken_ohlc_data(pair='ETHUSD', interval=60, since=None):
    url = 'https://api.kraken.com/0/public/OHLC'
    params = {
        'pair': pair,
        'interval': interval,
        'since': since
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['error']:
        print("Error:", data['error'])
        return None
    
    # Adjust to get the correct key from the result
    pair_key = list(data['result'].keys())[0]
    ohlc_data = data['result'][pair_key]
    
    df = pd.DataFrame(ohlc_data, columns=[
        'time', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'
    ])
    
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    return df

# Example usage
pair = 'ETHUSD'
interval = 60  # 1 hour interval
# Set 'since' to an old timestamp to get the maximum data possible in one call
since = int(time.time()) - (60 * 60 * 24 * 30 * 12)  # Approx. 1 year ago

eth_usd_data = fetch_kraken_ohlc_data(pair, interval, since)
print(eth_usd_data.head())
print(eth_usd_data.tail())

# Save the data to a CSV file for future use
eth_usd_data.to_csv('eth_usd_ohlc_data.csv', index=False)
