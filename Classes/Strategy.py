import yfinance as yf
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

class Strategy:
    def __init__(self, ticker, start_date, end_date, timeframe):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date      
        self.timeframe = timeframe

        # Columns - Open, High, Low, Close, Adj Close, Volume
        self.data = yf.download(ticker, start_date, end_date, progress=False)

    def simpleMovingAverage(self, period):
        """
        Returns the SMA for the given period
        
        [https://en.wikipedia.org/wiki/Moving_average#Simple_moving_average]
        """
        return self.data.rolling(window=period).mean()['Adj Close']
    
    def exponentialMovingAverage(self, period):
        """
        Returns the EMA (giving more weight to newer data) for the given period

        [https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average]
        """
        return self.data.ewm(span=period).mean()['Adj Close']
    
    def macd(self):
        """
        Returns the MACD (Moving Average Convergence / Divergence)for periods of 12 and 26
        
        [https://en.wikipedia.org/wiki/MACD]
        """
        return self.exponentialMovingAverage(12) - self.exponentialMovingAverage(26)

    def macd_signalLine(self):
        """Returns the signal line for the MACD which is an EMA of period 9"""
        return self.exponentialMovingAverage(9)

    def macd_histogram(self):
        """Returns the histogram for MACD"""
        return self.macd() - self.macd_signalLine()
    
    def bollingerBands(self, period, numsd):
        """
        Returns the average, upper and lower bands for Bollinger Bands
        
        [https://en.wikipedia.org/wiki/Bollinger_Bands]
        """
        df = pd.DataFrame()
        df['Average'] = self.data.rolling(window=period)['Adj Close'].mean()
        standard_deviation = self.data.rolling(window=period)['Adj Close'].std()
        df['Upper Band'] = df['Average'] + (standard_deviation * numsd)
        df['Lower Band'] = df['Average'] - (standard_deviation * numsd)

        return df

    def get_max_high_price(self):
        """Returns the max high price"""
        return np.round(self.data['High'].max(), 2)

    def get_min_low_price(self):
        """Returns the min low price"""
        return np.round(self.data['Low'].min(), 2)
    
    def get_max_close_price(self):
        """Returns the max close price"""
        return np.round(self.data['Adj Close'].max(), 2)
    
    def get_min_close_price(self):
        """Returns the min close price"""
        return np.round(self.data['Adj Close'].min(), 2)
    
    def vwap(self):
        """
        Returns Volume Weighted Average Price (VWAP)

        [https://en.wikipedia.org/wiki/Volume-weighted_average_price]
        
        """
        df = pd.DataFrame()
        # Calculate Typical Price
        df['TP'] = (self.data['Low'] + self.data['High'] + self.data['Close']) / 3
        df['VWAP'] = (df['TP'] * self.data['Volume']).cumsum() / self.data['Volume'].cumsum()
        
        return df['VWAP']
    
    def rsi(self, period=14):
        """
        Returns the Relative Strength Index using EMA with a default period of 14
        
        [https://en.wikipedia.org/wiki/Relative_strength_index]

        """
        df = pd.DataFrame()
        change = self.data['Adj Close'].diff()

        # Clip for days with positive price change
        up = change.clip(lower=0)

        # Clip for days with negative price change (* -1 to make it all positive for division purposes)
        down = -change.clip(upper=0)

        # Get moving averages for up and down data
        df['ma_up'] = up.ewm(span=period-1, adjust=True, min_periods=period).mean()
        df['ma_down'] = down.ewm(span=period-1, adjust=True, min_periods=period).mean()

        rsi = df['ma_up'] / df['ma_down']
        df['RSI'] = 100 - (100/(1+rsi))

        return df['RSI']
    
    def mfi(self, period=14):
        """
        Returns the Money Flow Index with a default period of 14

        [https://en.wikipedia.org/wiki/Money_flow_index]

        MFI = 100 - (100 / (1 + money ratio))

        where 
            money ratio = positive money flow / negative money flow
            positive money flow = added money flow of all days where typical price (TP) is higher than previous day's TP
            negative money flow = added money flow of all days where typical price (TP) is lower than previous day's TP
        """
        df = pd.DataFrame()
        # Calculate Typical Price
        df['TP'] = (self.data['Low'] + self.data['High'] + self.data['Close']) / 3
        # Calculate Raw Money Flow
        df['RMF'] = df['TP'] * self.data['Volume']
        # Calculate Money Flow Ratio where PMF = Positive Money Flow, NMF = Negative Money Flow

        # Calculate the change in typical price from the previous day
        df['change'] = df['TP'].diff()
        
        # Calculate the number of days that have a positive and negative change
        df['1PMF'] = df['RMF'].where(df['change'] >= 0).fillna(0)
        df['1NMF'] = df['RMF'].where(df['change'] < 0).fillna(0)

        df['14PMF'] = df['1PMF'].rolling(window=period).sum()
        df['14NMF'] = df['1NMF'].rolling(window=period).sum()

        df['Money Ratio'] = df['14PMF'] / df['14NMF']

        # Calculate MFI
        df['MFI'] = 100 - (100/(1+df['Money Ratio']))
        return df['MFI']

    
    def up_days(self):
        """
        Returns true if the day has a positive change from the previous day, otherwise false
        """
        change = self.data['Close'].diff()
        return change > 0
    
    def is_up_day(self, date):
        """
        Returns if the specified day had a positive change
        """
        change = self.data['Close'].diff()
        return change.loc[str(date)] > 0

if __name__ == '__main__':
    s = Strategy("AAPL", dt.date(2023,1,1), dt.date.today(), '1d')
    plt.figure()
    plt.title('Price data')
    plt.plot(s.data["Open"])

    plt.figure()
    plt.title('Indicators')
    plt.plot(s.mfi())
    plt.show()