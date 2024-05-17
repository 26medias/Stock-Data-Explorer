import pandas as pd
import numpy as np
from tqdm import tqdm
import math

class Trading:
    def __init__(self, initial_cash=50000000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}
        self.trades = []
        self.portfolio_values = []
        self.realized_profits = 0
        self.buy_count = 0
        self.sell_count = 0

    def buy(self, qty, price, ticker, datetime, trailingStop):
        cost = qty * price

        if self.cash >= cost:
            self.cash -= cost
            if ticker in self.positions:
                position = self.positions[ticker]
                total_qty = position['qty'] + qty
                avg_price = ((position['qty'] * position['avg_price']) + cost) / total_qty
                self.positions[ticker] = {'qty': total_qty, 'avg_price': avg_price, 'gains': 0, 'max_value': self.positions[ticker]['max_value'], 'trailingStop':trailingStop}
            else:
                self.positions[ticker] = {'qty': qty, 'avg_price': price, 'gains': 0, 'max_value': price, 'trailingStop':trailingStop}
            self.trades.append({'type': 'buy', 'ticker': ticker, 'qty': qty, 'price': price, 'datetime': datetime, 'gains': 0, 'label': 'buy'})
            self.buy_count += qty
            #print(f"[BUY] [{datetime}] [{ticker:5}] {price:8.2f}   (x{qty})")
        else:
            print("Not enough cash to buy")

    def sell(self, qty, price, ticker, datetime, label):
        if ticker in self.positions and self.positions[ticker]['qty'] >= qty:
            revenue = qty * price
            self.cash += revenue
            position = self.positions[ticker]
            remaining_qty = position['qty'] - qty
            gains = ((price - position['avg_price']) / position['avg_price']) * 100
            if remaining_qty == 0:
                del self.positions[ticker]
            else:
                self.positions[ticker] = {'qty': remaining_qty, 'avg_price': position['avg_price'], 'gains': gains, 'max_value': self.positions[ticker]['max_value']}
            self.trades.append({'type': 'sell', 'ticker': ticker, 'qty': qty, 'price': price, 'datetime': datetime, 'gains': gains, 'label': label})
            self.realized_profits += (price - position['avg_price']) * qty
            self.sell_count += qty
            #print(f"[SELL] [{datetime}] [{ticker:5}] {price:8.2f}   (x{qty})   {gains:8.2f}%")
        else:
            print("Not enough shares to sell or ticker not in portfolio")

    def calculate_stats(self, trades_df):
        if trades_df.empty:
            return pd.DataFrame()

        trades_df['datetime'] = pd.to_datetime(trades_df['datetime'])
        trades_df = trades_df.sort_values(by='datetime')
        trades_df['cum_gains'] = (1 + trades_df['gains'] / 100).cumprod() - 1

        total_trades = len(trades_df)
        winning_trades = trades_df[trades_df['gains'] > 0]
        losing_trades = trades_df[trades_df['gains'] <= 0]
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        loss_rate = len(losing_trades) / total_trades if total_trades > 0 else 0
        avg_gain = winning_trades['gains'].mean() if not winning_trades.empty else 0
        avg_loss = losing_trades['gains'].mean() if not losing_trades.empty else 0
        win_loss_ratio = avg_gain / abs(avg_loss) if avg_loss != 0 else np.inf
        profit_factor = winning_trades['gains'].sum() / abs(losing_trades['gains'].sum()) if losing_trades['gains'].sum() != 0 else np.inf

        # Calculate alpha, beta, Sharpe ratio, etc.
        returns = trades_df['gains'] / 100
        risk_free_rate = 0.01  # Example risk-free rate
        excess_returns = returns - risk_free_rate / len(returns)
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else np.inf
        annualized_sharpe = sharpe_ratio * np.sqrt(252)  # Assuming daily returns

        # Example: Use S&P 500 returns as market returns for beta calculation
        market_returns = np.random.normal(0.0005, 0.01, len(returns))  # Replace with actual market returns
        beta = np.cov(returns, market_returns)[0, 1] / np.var(market_returns) if np.var(market_returns) != 0 else np.inf
        alpha = np.mean(excess_returns) - beta * np.mean(market_returns) if beta != np.inf else np.inf

        # Track portfolio value over time
        portfolio_values_df = pd.DataFrame(self.portfolio_values, columns=['datetime', 'cash', 'invested_value', 'portfolio_value', 'unrealized_profits', 'total_value', 'total_gains', 'unrealized_gains', 'buy_count', 'sell_count'])

        # Debug: Inspect the portfolio_value column before conversion
        #print(portfolio_values_df['portfolio_value'])

        # Ensure all values in 'portfolio_value' are numeric
        #portfolio_values_df['portfolio_value'] = pd.to_numeric(portfolio_values_df['portfolio_value'], errors='coerce')

        stats = {
            'initial_cash': self.initial_cash,
            'final_cash': self.cash,
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'SL': len(trades_df[trades_df['label'] == 'SL']),
            'TS': len(trades_df[trades_df['label'] == 'TS']),
            'Open': len(trades_df[trades_df['label'] == 'Open']),
            'profit_loss': self.cash - self.initial_cash,
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'avg_gain': avg_gain,
            'avg_loss': avg_loss,
            'win_loss_ratio': win_loss_ratio,
            'profit_factor': profit_factor,
            'sharpe_ratio': annualized_sharpe,
            'alpha': alpha,
            'beta': beta
        }
        stats_df = pd.DataFrame([stats])

        # Format stats for better readability
        stats_df['initial_cash'] = stats_df['initial_cash'].map('${:,.2f}'.format)
        stats_df['final_cash'] = stats_df['final_cash'].map('${:,.2f}'.format)
        stats_df['profit_loss'] = stats_df['profit_loss'].map('${:,.2f}'.format)
        stats_df['avg_gain'] = stats_df['avg_gain'].map('{:.2f}%'.format)
        stats_df['avg_loss'] = stats_df['avg_loss'].map('{:.2f}%'.format)
        stats_df['win_loss_ratio'] = stats_df['win_loss_ratio'].map('{:.2f}'.format)
        stats_df['profit_factor'] = stats_df['profit_factor'].map('{:.2f}'.format)
        stats_df['sharpe_ratio'] = stats_df['sharpe_ratio'].map('{:.2f}'.format)
        stats_df['alpha'] = stats_df['alpha'].map('{:.2f}'.format)
        stats_df['beta'] = stats_df['beta'].map('{:.2f}'.format)

        return stats_df, portfolio_values_df


    def extendRow(self, current_data):
        df = current_data.copy()
        if self.positions:
            positions_df = pd.DataFrame.from_dict(self.positions, orient='index')
            df = df.merge(positions_df, left_on='Ticker', right_index=True, how='left')
            df["invested"] = df["qty"]*df["avg_price"]
            df["value"] = df["qty"]*df["Close"]
            df["gains_value"] = df["value"]-df["invested"]
            df["gains"] = ((df['Close'] - df['avg_price']) / df['avg_price']) * 100
            #df["max"] = df[["max", "Close"]].max(axis=1) #max(df["max"], df['Close'])
            df["gainsFromMax"] = ((df['Close'] - df['max_value']) / df['max_value']) * 100
        return df

    def trade(self, symbols, data, onTick):
        filtered_data = data[data['Ticker'].isin(symbols)]
        filtered_data = filtered_data.sort_index()

        unique_dates = filtered_data.index.unique()

        invested_value = 0
        unrealized_profits = 0
        portfolio_value = 0
        current_gains_percent = 0
    
        for current_date in tqdm(unique_dates):
            current_data = filtered_data.loc[current_date]
            pre_tick_data = self.extendRow(current_data)
            self.buy_count = 0
            self.sell_count = 0

            prev_row = None
            if isinstance(pre_tick_data, pd.DataFrame):
                for _, row in pre_tick_data.iterrows():
                    ticker = row['Ticker']
                    if ticker in self.positions:
                        self.positions[ticker]['gains'] = ((row['Close'] - self.positions[ticker]['avg_price']) / self.positions[ticker]['avg_price']) * 100
                        self.positions[ticker]['max_value'] = max(row['Close'], self.positions[ticker]['max_value'])
                    position = self.positions.get(ticker, {'qty': 0, 'avg_price': 0, 'gains': 0})
                    onTick(self, row, prev_row, position)
                    prev_row = row
            else:
                ticker = pre_tick_data['Ticker']
                if ticker in self.positions:
                    self.positions[ticker]['gains'] = ((pre_tick_data['Close'] - self.positions[ticker]['avg_price']) / self.positions[ticker]['avg_price']) * 100
                    self.positions[ticker]['max_value'] = max(row['Close'], self.positions[ticker]['max_value'])
                position = self.positions.get(ticker, {'qty': 0, 'avg_price': 0, 'gains': 0})
                onTick(self, pre_tick_data, prev_row, position)
            
            invested_value = 0
            unrealized_profits = 0
            portfolio_value = 0
            current_gains_percent = 0

            after_tick_data = self.extendRow(current_data)
            if self.positions:
                invested_value = after_tick_data["invested"].sum(skipna=True)
                unrealized_profits = after_tick_data["gains_value"].sum(skipna=True)
                portfolio_value = after_tick_data["value"].sum(skipna=True)
                current_gains_percent = (portfolio_value-invested_value)/invested_value*100

            total_value = self.cash + portfolio_value
            gains_percent = ((total_value - self.initial_cash) / self.initial_cash) * 100
            self.portfolio_values.append((current_date, self.cash, invested_value, portfolio_value, unrealized_profits, total_value, gains_percent, current_gains_percent, self.buy_count, self.sell_count))

        # Close all open positions at the last available price
        open_pos = after_tick_data[after_tick_data['qty'] > 0]
        for _, row in open_pos.iterrows():
            print(f"Closing {row['Ticker']}: ${row['avg_price']} -> ${row['Close']} ({row['gains']}% x{row['qty']})")
            self.sell(qty=row['qty'], price=row['Close'], ticker=row['Ticker'], datetime=row.name, label="Open")

        positions_df = pd.DataFrame.from_dict(self.positions, orient='index')
        trades_df = pd.DataFrame(self.trades)
        stats_df, portfolio_values_df = self.calculate_stats(trades_df)
        return positions_df, trades_df, stats_df, portfolio_values_df
