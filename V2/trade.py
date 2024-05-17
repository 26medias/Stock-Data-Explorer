import pandas as pd
from Trading import Trading
from DataChart import DataChart

def query_signal(file_path='./cache/1d_extended.pkl', threshold=10):
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
    
    if row['SIGNAL'] <= 10 and position['qty'] < 3: # and prev_row is not None and 'SIGNAL' in prev_row and prev_row['SIGNAL'] > 10:
        trading_instance.buy(qty=1, price=row['Close'], ticker=row['Ticker'], datetime=row.name)
    
    if position['qty'] > 0:
        gains = ((row['Close'] - position['avg_price']) / position['avg_price']) * 100
        if gains >= 4 or gains <= -2.5:
            if gains <= -2.5:
                close_price = position['avg_price'] * (100-5)/100
            else:
                close_price = row['Close']
            trading_instance.sell(qty=position['qty'], price=close_price, ticker=row['Ticker'], datetime=row.name)

def title(name):
    print(f"\n==== {name} ====")

def save(items):
    for item in items:
        item[0].to_pickle(item[1])

def main():
    file_path = './cache/1d_extended.pkl'
    threshold = 10
    filtered_data = query_signal(file_path, threshold)
    
    if not filtered_data.empty:
        stats = generate_stats(filtered_data)
        print(stats)
    else:
        print("No data found matching the criteria.")


    symbols = filtered_data['Ticker'].unique()

    print("SYMBOLS: ", len(symbols), symbols)

    data = pd.read_pickle(file_path)

    trader = Trading(initial_cash=50000)
    positions, trades, stats, portfolio_values = trader.trade(
        symbols=symbols[:50],
        data=data,
        onTick=ontick_func
    )

    title("Positions")
    print(positions)
    title("trades")
    print(trades)
    title("stats")
    print(stats)
    title("portfolio_values")
    print(portfolio_values)

    save([
        [positions, './cache/_positions_1d.pkl'],
        [trades, './cache/_trades_1d.pkl'],
        [stats, './cache/_stats_1d.pkl'],
        [portfolio_values, './cache/_portfolio_values_1d.pkl']
    ])

    """
    # Ensure datetime column is in datetime format
    portfolio_values['datetime'] = pd.to_datetime(portfolio_values['datetime'])
    #portfolio_values = portfolio_values.sort_values(by='datetime')
    portfolio_values.set_index('datetime', inplace=True)
    portfolio_values.to_pickle('cache/trading-latest.pkl')

    chart = DataChart(portfolio_values)
    chart.plot_subplots([
        ['cash', 'portfolio_value', 10000],
        ['realized_profits', 'unrealized_profits'],
        ['gains%'],
        ['invested_value']
    ], OHLC=False)
    """

if __name__ == '__main__':
    main()
