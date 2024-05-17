import pandas as pd
import numpy as np

class Trading:
    def __init__(self, initial_cash=50000000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}
        self.trades = []
        self.portfolio_values = []

    def buy(self, qty, price, ticker, datetime):
        cost = qty * price

        if self.cash >= cost:
            self.cash -= cost
            if ticker in self.positions:
                position = self.positions[ticker]
                total_qty = position['qty'] + qty
                avg_price = ((position['qty'] * position['avg_price']) + cost) / total_qty
                self.positions[ticker] = {'qty': total_qty, 'avg_price': avg_price, 'gains': 0}
            else:
                self.positions[ticker] = {'qty': qty, 'avg_price': price, 'gains': 0}
            self.trades.append({'type': 'buy', 'ticker': ticker, 'qty': qty, 'price': price, 'datetime': datetime})
            #print(f"[BUY] [{datetime}] [{ticker:5}] {price:8.2f}   (x{qty})")
        else:
            print("Not enough cash to buy")

    def sell(self, qty, price, ticker, datetime):
        if ticker in self.positions and self.positions[ticker]['qty'] >= qty:
            revenue = qty * price
            self.cash += revenue
            position = self.positions[ticker]
            remaining_qty = position['qty'] - qty
            gains = ((price - position['avg_price']) / position['avg_price']) * 100
            if remaining_qty == 0:
                del self.positions[ticker]
            else:
                self.positions[ticker] = {'qty': remaining_qty, 'avg_price': position['avg_price'], 'gains': gains}
            self.trades.append({'type': 'sell', 'ticker': ticker, 'qty': qty, 'price': price, 'datetime': datetime, 'gains': gains})
            print(f"[SELL] [{datetime}] [{ticker:5}] {price:8.2f}   (x{qty})   {gains:8.2f}%")
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
        portfolio_values_df = pd.DataFrame(self.portfolio_values, columns=['datetime', 'cash', 'realized_profits', 'unrealized_profits', 'gains%', 'invested_value', 'portfolio_value'])
        portfolio_values_df['portfolio_value'] = portfolio_values_df['portfolio_value'].astype(float)

        stats = {
            'initial_cash': self.initial_cash,
            'final_cash': self.cash,
            'total_trades': total_trades,
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

    def trade(self, symbols, data, onTick):
        filtered_data = data[data['Ticker'].isin(symbols)]
        filtered_data = filtered_data.sort_index()
        realized_profits = 0

        for idx, row in filtered_data.iterrows():
            ticker = row['Ticker']
            if ticker in self.positions:
                self.positions[ticker]['gains'] = ((row['Close'] - self.positions[ticker]['avg_price']) / self.positions[ticker]['avg_price']) * 100
            position = self.positions.get(ticker, {'qty': 0, 'avg_price': 0, 'gains': 0})
            prev_row = self.positions[ticker] if ticker in self.positions else None
            onTick(self, row, prev_row, position)

            # Track portfolio value
            invested_value = sum([p['qty'] * row['Close'] for p in self.positions.values()])
            unrealized_profits = invested_value - sum([p['qty'] * p['avg_price'] for p in self.positions.values()])
            total_value = self.cash + invested_value
            gains_percent = ((total_value - self.initial_cash) / self.initial_cash) * 100
            self.portfolio_values.append((idx, self.cash, realized_profits, unrealized_profits, gains_percent, invested_value, total_value))

            # Save stats every 10,000 rows
            if len(self.portfolio_values) % 10000 == 0:
                positions_df = pd.DataFrame.from_dict(self.positions, orient='index')
                trades_df = pd.DataFrame(self.trades)
                stats_df, portfolio_values_df = self.calculate_stats(trades_df)
                portfolio_values_df.to_pickle(f'cache/trading-latest_{len(self.portfolio_values)}.pkl')
                stats_df.to_pickle(f'cache/stats-latest_{len(self.portfolio_values)}.pkl')
                print(f"Processed {len(self.portfolio_values)} rows")

        # Close all open positions at the last available price
        last_row = filtered_data.iloc[-1]
        for ticker, position in list(self.positions.items()):
            if position['qty'] > 0:
                realized_profits += ((last_row['Close'] - position['avg_price']) * position['qty'])
                self.sell(qty=position['qty'], price=last_row['Close'], ticker=ticker, datetime=last_row.name)

        positions_df = pd.DataFrame.from_dict(self.positions, orient='index')
        trades_df = pd.DataFrame(self.trades)
        stats_df, portfolio_values_df = self.calculate_stats(trades_df)
        return positions_df, trades_df, stats_df, portfolio_values_df
