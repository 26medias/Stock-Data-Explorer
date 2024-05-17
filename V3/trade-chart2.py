import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure()
        self.ax_cash = self.fig.add_subplot(511)
        self.ax_portfolio_value = self.fig.add_subplot(512, sharex=self.ax_cash)
        self.ax_realized_profits = self.fig.add_subplot(513, sharex=self.ax_cash)
        self.ax_unrealized_profits = self.fig.add_subplot(514, sharex=self.ax_cash)
        self.ax_invested_value = self.fig.add_subplot(515, sharex=self.ax_cash)
        
        super().__init__(self.fig)
        self.setParent(parent)

    def plot(self, data):
        self.ax_cash.clear()
        self.ax_portfolio_value.clear()
        self.ax_realized_profits.clear()
        self.ax_unrealized_profits.clear()
        self.ax_invested_value.clear()
        
        self.ax_cash.plot(data.index, data['cash'], label='Cash')
        self.ax_cash.legend()
        self.ax_cash.grid()

        self.ax_portfolio_value.plot(data.index, data['portfolio_value'], label='Portfolio Value')
        self.ax_portfolio_value.legend()
        self.ax_portfolio_value.grid()

        self.ax_realized_profits.plot(data.index, data['realized_profits'], label='Realized Profits')
        self.ax_realized_profits.legend()
        self.ax_realized_profits.grid()

        self.ax_unrealized_profits.plot(data.index, data['unrealized_profits'], label='Unrealized Profits')
        self.ax_unrealized_profits.legend()
        self.ax_unrealized_profits.grid()

        self.ax_invested_value.plot(data.index, data['invested_value'], label='Invested Value')
        self.ax_invested_value.legend()
        self.ax_invested_value.grid()

        self.fig.tight_layout()
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Portfolio Chart')
        self.setGeometry(100, 100, 1200, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        self.plot_canvas = PlotCanvas(self.central_widget)
        layout.addWidget(self.plot_canvas)

    def update_plot(self, data):
        self.plot_canvas.plot(data)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    portfolio_values = pd.read_pickle('cache/trading-latest.pkl')
    main_window.update_plot(portfolio_values)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
