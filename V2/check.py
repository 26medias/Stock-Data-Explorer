import pandas as pd

pd.set_option('display.max_rows',5000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 20000)

data = pd.read_pickle("cache/1d_extended.pkl")
print(data.tail(200))