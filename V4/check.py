import pandas as pd

pd.set_option('display.max_rows',5000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 20000)

data = pd.read_pickle("cache/1d_extended_latest.pkl")


latest_datetime = data.index.max()
print(latest_datetime)


# Filter the DataFrame to keep only the rows with the latest datetime
latest_df = data[data.index == latest_datetime]

# Set 'Ticker' as the index
latest_df.set_index('Ticker', inplace=True)

print("")
print("")
print(latest_df)
