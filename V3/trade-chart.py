import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# Load your data
portfolio_values = pd.read_pickle('cache/_portfolio_values_1d.pkl')
portfolio_values.set_index('datetime', inplace=True)

# Initialize the Dash app
app = Dash(__name__)

# Define the app layout
app.layout = html.Div([
    dcc.Graph(id='portfolio-graph'),
    dcc.RangeSlider(
        id='date-slider',
        min=0,
        max=len(portfolio_values) - 1,
        value=[0, len(portfolio_values) - 1],
        marks={i: date.strftime('%Y-%m-%d') for i, date in enumerate(portfolio_values.index[::len(portfolio_values) // 10])}
    )
])

# Define the callback to update the graph
@app.callback(
    Output('portfolio-graph', 'figure'),
    Input('date-slider', 'value')
)
def update_graph(date_range):
    filtered_data = portfolio_values.iloc[date_range[0]:date_range[1]]

    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.02,
                        subplot_titles=('Cash', 'Portfolio Value', 'Realized Profits', 'Unrealized Profits', 'Invested Value'))

    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['cash'], name='Cash'), row=1, col=1)
    #fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['total_value'], name='Total Value'), row=1, col=1)
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['portfolio_value'], name='Portfolio Value'), row=2, col=1)
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['unrealized_profits'], name='Unrealized Profits'), row=3, col=1)
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['invested_value'], name='Invested Value'), row=4, col=1)

    fig.update_layout(height=800, showlegend=False)

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


