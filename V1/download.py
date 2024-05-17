from DataFetcher import DataFetcher
from DataLoader import DataLoader
from DataChart import DataChart
from ma import MovingAverageExtender

import requests
from bs4 import BeautifulSoup

def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text.strip()
        tickers.append(ticker)
    return tickers

if __name__ == '__main__':
    fetcher = DataFetcher()
    sp500_tickers = get_sp500_tickers()
    print(sp500_tickers)
    
    fetcher.fetch_all(sp500_tickers)