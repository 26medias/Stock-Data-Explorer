class DataLoader:
    def __init__(self, fetcher, extender_class=None):
        self.fetcher = fetcher
        self.extender_class = extender_class

    def load_data(self, ticker):
        data = self.fetcher.fetch_data(ticker)
        if self.extender_class:
            extender = self.extender_class(data)
            data = extender.extend_data()
        return data
