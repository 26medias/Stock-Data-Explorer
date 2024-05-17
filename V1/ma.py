class MovingAverageExtender:
    def __init__(self, data, window=200):
        self.data = data
        self.window = window

    def extend_data(self):
        self.data[f'MA{self.window}'] = self.data['Close'].rolling(window=self.window).mean()
        return self.data
