import pandas as pd

class HelperTA:

    def Stochastic(self, data, period=14):
        low = data.rolling(window=period).min()
        high = data.rolling(window=period).max()
        k_percent = 100 * ((data - low) / (high - low))
        return k_percent

    def RSI(self, data, period=14):
        delta = data.diff()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        roll_up = up.ewm(span=period).mean()
        roll_down = down.abs().ewm(span=period).mean()
        RS = roll_up / roll_down
        RSI = 100.0 - (100.0 / (1.0 + RS))
        return RSI

    def stockRSI(self, data, K=5, D=5, rsiPeriod=20, stochPeriod=3):
        rsi = self.RSI(data, period=rsiPeriod)
        stoch = self.Stochastic(rsi, period=stochPeriod)
        k = stoch.rolling(window=K).mean()
        d = k.rolling(window=D).mean()
        return (k, d)

    def DCO(self, data, donchianPeriod=20, smaPeriod=3):
        lower = data.rolling(window=donchianPeriod).min()
        upper = data.rolling(window=donchianPeriod).max()
        DCO = (data - lower) / (upper - lower) * 100
        s = DCO.rolling(window=smaPeriod).mean()
        return (DCO, s)

    def MarketCycle(self, donchianPrice, rsiPrice, srsiPrice, donchianPeriod, donchianSmoothing, rsiPeriod, rsiSmoothing, srsiPeriod, srsiSmoothing, srsiK, srsiD, rsiWeight, srsiWeight, dcoWeight):
        DCO, DCOs = self.DCO(donchianPrice, donchianPeriod, donchianSmoothing)
        rsiValue = self.RSI(rsiPrice, rsiPeriod)
        rsiK = rsiValue.rolling(window=rsiSmoothing).mean()
        k, d = self.stockRSI(srsiPrice, srsiK, srsiD, srsiPeriod, srsiSmoothing)
        aggr = ((DCO + DCOs) * dcoWeight + (rsiValue + rsiK) * rsiWeight + (k + d) * srsiWeight) / (2 * (dcoWeight + rsiWeight + srsiWeight))
        return aggr

class MarketCycleExtender:
    def __init__(self, data):
        self.data = data
        self.hta = HelperTA()

    def std(self, data, min_value=0, max_value=100, window=200):
        min_col = data.rolling(window=window).min()
        max_col = data.rolling(window=window).max()
        return (data - min_col) / (max_col - min_col) * (max_value - min_value) + min_value

    def std_with_zero_center(self, data, min_value=0, max_value=100, window=200):
        abs_min_col = data.rolling(window=window).apply(lambda x: min(abs(x.min()), abs(x.max())))
        abs_max_col = data.rolling(window=window).apply(lambda x: max(abs(x.min()), abs(x.max())))
        return data / abs_max_col * (max_value - min_value) / 2 + (max_value - min_value) / 2
    
    def mc(self, a, b):
        return self.hta.MarketCycle(self.data['Close'], self.data['Close'], self.data['Close'],
                                                        donchianPeriod=a, donchianSmoothing=3,
                                                        rsiPeriod=a, rsiSmoothing=3,
                                                        srsiPeriod=b, srsiSmoothing=3, srsiK=5, srsiD=5,
                                                        rsiWeight=0.5, srsiWeight=1, dcoWeight=1)

    

    def extend_data(self):
        a = 200
        b = 100
        self.data['50_MA'] = self.data['Close'].rolling(window=50).mean()
        self.data['100_MA'] = self.data['Close'].rolling(window=100).mean()
        self.data['200_MA'] = self.data['Close'].rolling(window=200).mean()
        self.data['50_MAOSC'] = self.std_with_zero_center(self.data['Close']-self.data['50_MA'], 0, 100, 50)
        self.data['100_MAOSC'] = self.std_with_zero_center(self.data['Close']-self.data['100_MA'], 0, 100, 100)
        self.data['200_MAOSC'] = self.std_with_zero_center(self.data['Close']-self.data['200_MA'], 0, 100, 200)
        
        self.data['long_MarketCycle'] = self.mc(200, 200)
        self.data['med_MarketCycle'] = self.mc(100, 100)
        self.data['short_MarketCycle'] = self.mc(50, 50)
        self.data['avg_MarketCycle'] = (self.data['long_MarketCycle'] + self.data['short_MarketCycle'] + self.data['short_MarketCycle']) / 3
        
        self.data['avg_MAOSC'] = (self.data['50_MAOSC'] + self.data['100_MAOSC'] + self.data['200_MAOSC']) / 3
        #self.data['avg_MAOSC'] = ((self.data['Close']-self.data['50_MA']) + (self.data['Close']-self.data['100_MA']) + self.data['Close']-self.data['200_MA']) / 3
        
        self.data['DCO'], self.data['DCO_s'] = self.hta.DCO(self.data['Close'], donchianPeriod=200, smaPeriod=3)
        self.data['1D-change'] = self.data['Close'].pct_change(periods=1) * 100
        self.data['5D-change'] = self.data['Close'].pct_change(periods=5) * 100
        self.data['20D-change'] = self.data['Close'].pct_change(periods=20) * 100

        # Create 'price-20d' column
        self.data['price-20d'] = self.data['Close'].shift(-20)

        # Create 'max-gains-20d' and 'max-loss-20d' columns
        self.data['max-gains-20d'] = self.data['Close'].rolling(window=20).apply(lambda x: ((x.max() - x[0]) / x[0]) * 100, raw=True).shift(-19)
        self.data['max-loss-20d'] = self.data['Close'].rolling(window=20).apply(lambda x: ((x.min() - x[0]) / x[0]) * 100, raw=True).shift(-19)

        self.data["SIGNAL"] = (self.data['avg_MAOSC'] + self.data['DCO'] + self.data['med_MarketCycle']) / 3
        
        return self.data
