from StockData import StockData

if __name__ == '__main__':
    stock_data = StockData()
    # Refresh all data with 1h interval
    stock_data.RefreshAll(interval='1d')
    # Get data for a specific symbol with 1h interval
    msft_data = stock_data.get('MSFT', interval='1d')
    print(msft_data.head())
    # Get all data with 1h interval
    all_data = stock_data.getAll(interval='1d')
    print(all_data.head())
