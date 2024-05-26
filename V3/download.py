from StockData import StockData
from MarketCycleExtender import MarketCycleExtender

if __name__ == '__main__':
    stock_data = StockData(period="10y")
    stock_data.tickers = ['ETH-USD','BTC-USD','DOGE-USD']
    # Refresh all data with 1h interval
    stock_data.RefreshAll(interval='1d')
    combined_data = stock_data.extend_and_combine(interval='1d', extender_class=MarketCycleExtender)
    stock_data._save_data(combined_data, f'1d_eth_extended_latest.pkl')
    # Get data for a specific symbol with 1h interval
    msft_data = stock_data.get('ETH-USD', interval='1d')
    print(msft_data.head())
    # Get all data with 1h interval
    all_data = stock_data.getAll(interval='1d')
    print(all_data.head())
