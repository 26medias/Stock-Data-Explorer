import pandas as pd
from StockData import StockData
from Charting import Charting

pd.set_option('display.max_rows',5000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 20000)

symbol = "TTWO"

#stock_data = StockData()
#data = stock_data.get('MSFT', interval='1d')
data = pd.read_pickle("cache/1d_extended_10y.pkl")
data = data[data["Ticker"] == symbol]
data["datetime"] = data.index
positions = pd.read_pickle("cache/_trades_1d.pkl")
positions = positions[positions['ticker']==symbol]
print(positions.tail(20))
print(data.tail(20))
merged_df = pd.merge(data, positions, on='datetime', how='left')
merged_df['qty'] = merged_df['qty'].fillna(0)

print(merged_df.tail(20))

chart = Charting(merged_df)
chart.plot_subplots([
    ["Close", "50_MA", "100_MA", "200_MA"],
    ["qty"],
    ['50_MAOSC', '100_MAOSC', 20, 50, 80],
    ['long_MarketCycle', 'med_MarketCycle', 'short_MarketCycle', 'avg_MarketCycle', 10, 50, 90],
    ['DCO', 'DCO_s', 20, 50, 80],
    ['SIGNAL', 10, 50, 90]
])
chart.run()

"""
"""