import yfinance as yf
import pandas as pd
import datetime as dt

class YFinanceData(object):
    def get_data(self, ticker, start_date, end_date, interval):
        ticker = yf.Ticker(ticker)
        aapl_historical = ticker.history(start=start_date, end=end_date, interval=interval, actions=False)
        print(aapl_historical)

    def get_daily_percentage_change(self, ticker, start_date, end_date, interval):
        data = self.get_data(ticker, start_date, end_date, interval)
        percentage_changes = []
        # for d in range(len(data)):

start = dt.date(2020, 1, 1)
end = dt.date.today()
ticker = "AAPL"
df = yf.download(ticker,start,end,interval="1d")
# Open, High, Low, Close, Adj Close, Volume
print(df)