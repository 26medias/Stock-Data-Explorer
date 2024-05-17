import pandas as pd
from Trading import Trading
from DataChart import DataChart

def main():
    portfolio_values = pd.read_pickle('cache/trading-latest.pkl')
    
    print(portfolio_values)

    chart = DataChart(portfolio_values)
    chart.plot_subplots([
        ['cash', 'portfolio_value', 50000000],
        ['realized_profits', 'unrealized_profits'],
        ['gains%'],
        ['invested_value']
    ], OHLC=False)

if __name__ == '__main__':
    main()
