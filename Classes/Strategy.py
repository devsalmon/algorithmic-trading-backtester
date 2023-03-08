import yfinance as yf
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

class Strategy:
    def __init__(self, ticker, start_date, end_date, timeframe):  
        self.start_date = start_date
        self.end_date   = end_date      
        self.timeframe  = timeframe

        # Columns - Open, High, Low, Close, Adj Close, Volume
        self.data = yf.download(ticker, start_date, end_date, progress=False)

    def simpleMovingAverage(self, period):
        """Returns the SMA for the given period"""
        return self.data.rolling(window=period).mean()['Adj Close']
    
    def exponentialMovingAverage(self, period):
        """Returns the EMA (giving more weight to newer data) for the given period"""
        return self.data.ewm(span=period).mean()['Adj Close']
    
    def macd(self):
        """Returns the MACD for periods of 12 and 26"""
        return self.exponentialMovingAverage(12) - self.exponentialMovingAverage(26)

    def macd_signalLine(self):
        """Returns the signal line for the MACD which is an EMA of period 9"""
        return self.exponentialMovingAverage(9)

    def macd_histogram(self):
        """Returns the histogram for MACD"""
        return self.macd() - self.macd_signalLine()
    
    def bollingerBands(self, period, numsd):
        """Returns the average, upper and lower bands for Bollinger Bands"""
        bb_data = pd.DataFrame()
        bb_data['Average'] = self.data.rolling(window=period)['Adj Close'].mean()
        standard_deviation = self.data.rolling(window=period)['Adj Close'].std()
        bb_data['Upper Band'] = bb_data['Average'] + (standard_deviation * numsd)
        bb_data['Lower Band'] = bb_data['Average'] - (standard_deviation * numsd)

        return bb_data

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
        """Returns the max close price"""
        return np.round(self.data['Adj Close'].min(), 2)
    
    def vwap(self):
        """Returns Volume Weighted Average Price"""

        df = pd.DataFrame()
        # Calculate Typical Price
        df['TP'] = (self.data['Low'] + self.data['High'] + self.data['Close']) / 3
        df['VWAP'] = (df['TP'] * self.data['Volume']).cumsum() / self.data['Volume'].cumsum()
        
        return df['VWAP']

if __name__ == '__main__':
    s = Strategy("AAPL", dt.date(2023,1,1), dt.date.today(), '1d')
    plt.plot(s.data["Open"])
    plt.plot(s.vwap())
    plt.show()