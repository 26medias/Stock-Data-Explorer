import pandas as pd

from StockData import StockData
from MarketCycle2Extender import MarketCycleExtender

if __name__ == '__main__':
    stock_data = StockData(period="1y")
    stock_data.tickers = ['AMC', 'GME', 'NVDA', 'ETH-USD','BTC-USD','DOGE-USD']
    # Refresh all data with 1h interval
    response = stock_data.RefreshAll(interval='1h')

    print(response.tail(50))

    combined_data = stock_data.extend_and_combine(interval='1h', extender_class=MarketCycleExtender)
    stock_data._save_data(combined_data, f'1h_extended_latest.pkl')
    
    data = pd.read_pickle("cache/1h_extended_latest.pkl")

    latest_datetime = data.index.max()


    # Filter the DataFrame to keep only the rows with the latest datetime
    latest_df = data[data.index == latest_datetime]

    # Set 'Ticker' as the index
    latest_df.set_index('Ticker', inplace=True)

    print(data.tail(50))
    print("")
    print(latest_datetime)
    print("")
    stats = data.describe()
    print(stats.T)
    print("")
    print("")
    print(latest_df)

