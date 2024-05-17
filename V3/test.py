from StockData import StockData  # Make sure to replace with the actual file name
from MarketCycleExtender import MarketCycleExtender
from DataChart import DataChart

def main():
    stock_data = StockData()

    # Get data for a specific symbol with 1h interval
    msft_data = stock_data.get('ALLE', interval='1h')
    
    # Extend data with additional calculations
    extender = MarketCycleExtender(msft_data)
    extended_data = extender.extend_data()
    print(extended_data)
    
    # Plot the data
    chart = DataChart(extended_data)
    chart.plot_subplots([
        ['50_MA', '100_MA', '200_MA'],
        ['SIGNAL', 10, 50, 90],
        ['avg_MarketCycle', 10, 50, 90],
        ['avg_MAOSC', 0],
        ['DCO', 10, 50, 90]
    ])

if __name__ == '__main__':
    main()
