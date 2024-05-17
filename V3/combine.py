from StockData import StockData  # Make sure to replace with the actual file name
from MarketCycleExtender import MarketCycleExtender
from DataChart import DataChart

def main():
    stock_data = StockData(period="1y")

    combined_data = stock_data.extend_and_combine(interval='1d', extender_class=MarketCycleExtender, range=[None,201])
    
    print(combined_data.head())

    stock_data._save_data(combined_data, f'1d_extended_1y.pkl')

if __name__ == '__main__':
    main()
