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
    
    def bollingerBands(self, length):
        average = self.data.rolling(window=length)['Adj Close'].mean()
        standard_deviation = self.data.rolling(window=length)['Adj Close'].std()
        upper_band = average + (standard_deviation * 2)
        lower_band = average - (standard_deviation * 2)

        return average, upper_band, lower_band


if __name__ == '__main__':
    s = Strategy("AAPL", dt.date(2023,1,1), dt.date.today(), '1d')

    # sma10 = s.simpleMovingAverage(10)
    plt.plot(s.data["Open"])
    average, upper_band, lower_band = s.bollingerBands(1)[0], s.bollingerBands(1)[1], s.bollingerBands(1)[2]
    plt.plot(average)
    plt.plot(upper_band)
    plt.plot(lower_band)
    plt.show()