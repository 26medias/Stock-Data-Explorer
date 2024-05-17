import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

class Charting:
    def __init__(self, data):
        self.data = data
        self.data.set_index('datetime', inplace=True)
        self.app = Dash(__name__)
        self.app.layout = html.Div([
            dcc.Graph(id='portfolio-graph'),
            dcc.RangeSlider(
                id='date-slider',
                min=0,
                max=len(self.data) - 1,
                value=[0, len(self.data) - 1],
                marks={i: date.strftime('%Y-%m-%d') for i, date in enumerate(self.data.index[::len(self.data) // 10])}
            )
        ])

    def plot_subplots(self, indicators_list):
        self.indicators_list = indicators_list
        @self.app.callback(
            Output('portfolio-graph', 'figure'),
            Input('date-slider', 'value')
        )
        def update_graph(date_range):
            filtered_data = self.data.iloc[date_range[0]:date_range[1]]
            n_plots = len(self.indicators_list)
            fig = make_subplots(rows=n_plots, cols=1, shared_xaxes=True, vertical_spacing=0.02)
            for i, indicators in enumerate(self.indicators_list):
                for indicator in indicators:
                    if isinstance(indicator, str):
                        fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data[indicator], name=indicator), row=i + 1, col=1)
                    elif isinstance(indicator, (int, float)):
                        fig.add_trace(go.Scatter(x=filtered_data.index, y=[indicator] * len(filtered_data), name=str(indicator), line=dict(dash='dash')), row=i + 1, col=1)
            fig.update_layout(height=200 * n_plots, showlegend=False)
            return fig

    def run(self):
        self.app.run_server(debug=True)

if __name__ == '__main__':
    portfolio_values = pd.read_pickle('cache/_portfolio_values_1d.pkl')
    chart = Charting(portfolio_values)
    chart.plot_subplots([
        ['total_value', 50000],
        ['buy_count', 'sell_count'],
        ['cash', 50000],
        ['invested_value', 'portfolio_value', 0],
        ['unrealized_profits', 0],
        ['total_gains', 'unrealized_gains', 0]
    ])
    chart.run()
