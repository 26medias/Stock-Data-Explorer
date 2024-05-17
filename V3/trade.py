import pandas as pd
from Trading import Trading
from DataChart import DataChart

pd.set_option('display.max_rows',5000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 20000)


timeframe = '1d'
period = '10y'
signal_value = 20
SL = -5
TS = -5


def query_signal(file_path=f'./cache/{timeframe}_extended_{period}.pkl', threshold=10):
    try:
        # Load the extended data
        data = pd.read_pickle(file_path)
        
        # Filter rows where SIGNAL <= threshold
        filtered_data = data[data['SIGNAL'] <= threshold]
        
        return filtered_data
    except Exception as e:
        print(f"Error reading or processing {file_path}: {e}")
        return pd.DataFrame()

def generate_stats(data):
    stats = {}

    print(data.head(20))
    
    for column in data.columns:
        if column == 'Ticker':
            continue
        col_data = data[column]
        stats[column] = {
            'mean': col_data.mean(),
            'std': col_data.std(),
            'min': col_data.min(),
            'max': col_data.max(),
            '25%': col_data.quantile(0.25),
            '50% (median)': col_data.median(),
            '75%': col_data.quantile(0.75),
            'missing': col_data.isnull().sum()
        }
    
    return pd.DataFrame(stats)

def ontick_func(trading_instance, row, prev_row, position):
    
    #if "qty" in row and row["qty"] > 0:
    #    print("")
    #    print(row)
    if prev_row is not None and 'SIGNAL' in prev_row and prev_row['SIGNAL'] < signal_value and row['SIGNAL'] >= signal_value and position['qty'] < 2: # and prev_row is not None and 'SIGNAL' in prev_row and prev_row['SIGNAL'] > 10:
        trading_instance.buy(qty=1, price=row['Close'], ticker=row['Ticker'], datetime=row.name, trailingStop=-1)
    
    if position['qty'] > 0:
        if row["gains"] <= SL:
            close_price = position['avg_price'] * (100+SL)/100
            trading_instance.sell(qty=position['qty'], price=close_price, ticker=row['Ticker'], datetime=row.name, label="SL")
        elif row["gainsFromMax"] <= TS and row["gains"] > 0:
            close_price = row['Close'] # position['max'] * (100+(TS*1.05))/100
            trading_instance.sell(qty=position['qty'], price=close_price, ticker=row['Ticker'], datetime=row.name, label="TS")

def ontick_func_old(trading_instance, row, prev_row, position):
    
    # if "qty" in row and row["qty"] > 0:
    #     print(row)
    if row['SIGNAL'] <= signal_value and position['qty'] < 2: # and prev_row is not None and 'SIGNAL' in prev_row and prev_row['SIGNAL'] > 10:
        trading_instance.buy(qty=1, price=row['Close'], ticker=row['Ticker'], datetime=row.name, trailingStop=-1)
    
    if position['qty'] > 0:
        if row["gains"] <= SL:
            close_price = position['avg_price'] * (100+SL)/100
            trading_instance.sell(qty=position['qty'], price=close_price, ticker=row['Ticker'], datetime=row.name)
        elif row["gainsFromMax"] <= TS and row["gains"] > 0:
            close_price = row['Close'] # position['max'] * (100+(TS*1.05))/100
            trading_instance.sell(qty=position['qty'], price=close_price, ticker=row['Ticker'], datetime=row.name)



def title(name):
    print(f"\n==== {name} ====")

def save(items):
    for item in items:
        item[0].to_pickle(item[1])

def main():
    file_path = f'./cache/{timeframe}_extended_{period}.pkl'
    filtered_data = query_signal(file_path, signal_value)
    
    if not filtered_data.empty:
        stats = generate_stats(filtered_data)
        print(stats)
    else:
        print("No data found matching the criteria.")


    symbols = filtered_data['Ticker'].unique()

    print("SYMBOLS: ",  symbols)
    print("Symbols found: ", len(symbols))
    print("Signals found: ", len(filtered_data))

    data = pd.read_pickle(file_path)

    trader = Trading(initial_cash=50000)
    positions, trades, stats, portfolio_values = trader.trade(
        symbols=symbols,
        data=data,
        onTick=ontick_func
    )

    title("Positions")
    print(positions)
    title("trades")
    print(trades.tail(20))
    title("portfolio_values")
    print(portfolio_values.tail(20))
    title("stats")
    print(stats)

    save([
        [positions, f'./cache/_positions_{timeframe}_period.pkl'],
        [trades, f'./cache/_trades_{timeframe}_period.pkl'],
        [stats, f'./cache/_stats_{timeframe}_period.pkl'],
        [portfolio_values, f'./cache/_portfolio_values_{timeframe}_period.pkl']
    ])

if __name__ == '__main__':
    main()
