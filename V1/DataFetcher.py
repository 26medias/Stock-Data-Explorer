import yfinance as yf
import os
import pandas as pd
import pickle
from tqdm import tqdm
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self, cache_dir='./cache',  use_cache_only=False):
        self.use_cache_only = use_cache_only
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_data(self, ticker, interval='1h'):
        cache_file = os.path.join(self.cache_dir, f'{ticker}.pkl')
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            if not self.use_cache_only:
                start_date = (datetime.now() - timedelta(days=720)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
                new_data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
                if not new_data.empty:
                    data = pd.concat([data, new_data]).drop_duplicates()
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
        else:
            if self.use_cache_only:
                raise FileNotFoundError(f"Cache file for {ticker} not found.")
            start_date = (datetime.now() - timedelta(days=720)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)

        return data

    def fetch_all(self, tickers, interval='1h'):
        for ticker in tqdm(tickers, desc="Fetching data for tickers"):
            data = self.fetch_data(ticker, interval)
            print(f'Fetched {len(data)} data points for {ticker}')
