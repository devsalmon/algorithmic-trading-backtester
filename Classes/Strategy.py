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
        """Returns the SMA for the given period on the CLOSE price"""
        return self.data.rolling(window=period).mean()['Close']

if __name__ == '__main__':
    s = Strategy("AAPL", dt.date(2023,1,1), dt.date.today(), '1d')
    sma10 = s.simpleMovingAverage(10)
    plt.plot(s.data['Open'])
    plt.plot(sma10)
    plt.show()