from DataFetcher import DataFetcher
from DataLoader import DataLoader
from DataChart import DataChart
from ma import MovingAverageExtender
from MarketCycleExtender import MarketCycleExtender

def main():
    fetcher = DataFetcher(use_cache_only=True)
    loader = DataLoader(fetcher, extender_class=MarketCycleExtender)
    ticker = 'EXR'
    
    data = loader.load_data(ticker)
    print(data.head())  # Print the first few rows to verify data loading and extension
    
    chart = DataChart(data)
    chart.plot_subplots([
        ['50_MA', '100_MA', '200_MA'],
        ['SIGNAL', 10, 50, 90],
        #['short_MarketCycle', 'short_MarketCycle', 'med_MarketCycle', 'long_MarketCycle', 10, 50, 90],
        ['avg_MarketCycle', 10, 50, 90],
        #['50_MAOSC', '50_MAOSC', '100_MAOSC', '200_MAOSC', 10, 50, 90],
        ['avg_MAOSC', 0],
        ['DCO', 10, 50, 90]
    ])

if __name__ == '__main__':
    main()
