import pandas as pd
from StockData import StockData
from MarketCycleExtender import MarketCycleExtender

pd.set_option('display.max_rows',5000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 20000)

if __name__ == '__main__':
    stock_data = StockData(period="1y")
    # Refresh all data with 1h interval
    #stock_data.RefreshAll(interval='1d')
    combined_data = stock_data.extend_and_combine(interval='1d', extender_class=MarketCycleExtender)
    stock_data._save_data(combined_data, f'1d_extended_latest.pkl')
    
    combined_data = pd.read_pickle('cache/1d_extended_latest.pkl')

    latest_datetime = combined_data.index.max()
    print(latest_datetime)


    # Filter the DataFrame to keep only the rows with the latest datetime
    latest_df = combined_data[combined_data.index == latest_datetime]

    # Set 'Ticker' as the index
    latest_df.set_index('Ticker', inplace=True)

    print("")
    print("")
    print(latest_df) #[latest_df['SIGNAL'] <= 10]

