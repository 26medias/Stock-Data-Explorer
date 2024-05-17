from StockData import StockData  # Make sure to replace with the actual file name
from MarketCycleExtender import MarketCycleExtender
from DataChart import DataChart

def main():
    stock_data = StockData()

    combined_data = stock_data.extend_and_combine(interval='1d', extender_class=MarketCycleExtender)
    
    print(combined_data.head())

if __name__ == '__main__':
    main()
