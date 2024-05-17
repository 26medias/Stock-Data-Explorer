import os
import pandas as pd
import numpy as np
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

np.set_printoptions(formatter={'float': lambda x: "{0:0.5f}".format(x)}, linewidth=1200)
pd.set_option('display.float_format', lambda x: f'{x:,.5f}')
pd.set_option('display.max_rows',5000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

class StockData:
    def __init__(self, cache_dir='./cache'):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        self.tickers = self.get_sp500_tickers()

    def get_sp500_tickers(self):
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text.strip()
            tickers.append(ticker)
        return tickers

    def _save_data(self, data, filename):
        filepath = os.path.join(self.cache_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data.to_pickle(filepath)

    def _load_data(self, filename):
        filepath = os.path.join(self.cache_dir, filename)
        if os.path.exists(filepath):
            return pd.read_pickle(filepath)
        else:
            raise FileNotFoundError(f"Cache file {filename} not found.")

    def Refresh(self, symbol, interval='1h'):
        data = yf.download(symbol, period='max', interval=interval)
        data = data.dropna()  # Drop NA values
        self._save_data(data, f'{interval}/{symbol}.pkl')
        return data

    def RefreshAll(self, interval='1h'):
        start_date = (datetime.now() - timedelta(days=720)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        # Use yfinance to download data for all tickers at once
        data = yf.download(self.tickers, interval=interval, period="10y", group_by='ticker', threads=True) #start=start_date, 
        #data = data.dropna()  # Drop NA values
        
        # Save individual ticker data
        for ticker in self.tickers:
            ticker_data = data[ticker].dropna()  # Drop NA values for each ticker
            self._save_data(ticker_data, f'{interval}/{ticker}.pkl')
        
        # Save combined data
        self._save_data(data, f'{interval}.pkl')
        return data

    def get(self, symbol, interval='1h'):
        return self._load_data(f'{interval}/{symbol}.pkl')

    def getAll(self, interval='1h'):
        return self._load_data(f'{interval}.pkl')

    def extend_and_combine(self, interval='1h', extender_class=None):
        all_extended_data = []

        def process_ticker(ticker):
            data = self.get(ticker, interval=interval)
            if extender_class:
                extender = extender_class(data)
                extended_data = extender.extend_data()
                extended_data['Ticker'] = ticker
                return extended_data
            return data

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_ticker, ticker) for ticker in self.tickers]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Extending data for all tickers"):
                try:
                    result = future.result()
                    if result is not None:
                        all_extended_data.append(result)
                except Exception as e:
                    print(f"Error processing ticker: {e}")

        combined_data = pd.concat(all_extended_data)
        self._save_data(combined_data, f'{interval}_extended.pkl')
        return combined_data
