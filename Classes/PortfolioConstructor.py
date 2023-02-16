# This class takes in list of trades (from strategy class) and displays
# the value of the portfolio at any given day (timeseries).
# Use pandas time series dataframe.

# Input will be dataframes of:
# UTID:  Ticker:  Quantity:  Buy Date:  Sell Date:
# Output will be dataframe of:
# Date:  Value:

import yfinance as yf
import pandas as pd
import datetime as dt


# TODO - implement 'cash' column and leverage
class PortfolioConstructor():
    def __init__(self, trades):
        super().__init__()
        self.cashValue = 10_000
        #self.portfolioValue = 10_000
        # Get all different tickers traded and add to ticker set.
        self.tickers = set()
        # Get all unique tickers from trades.
        for trade in trades:
            utid, ticker, qty, leverage, buy_date, sell_date = trade
            if ticker not in self.tickers:
                self.tickers.add(ticker)
        # Set the dataframe columns to the tickers and a value and cash column.
        columns = list(self.tickers)
        columns.append('value')
        columns.append('cash')
        # Choose date range for backtesting with periods being how many days ahead.
        date = pd.bdate_range("20130102", periods=10)
        # Create your dataframe with date being the index and fill in values as 0.
        df = pd.DataFrame(index=date, columns = columns).fillna(0)
        # Overwrite cash column to begin with the initial cash.
        df['cash'] = self.cashValue
        # Get data for each traded ticker from yfinance between date ranges.
        data = yf.download(list(self.tickers),dt.date(2013,1,2),dt.date(2013,1,17), progress=False)
        # Set each value in the dataframe with the quantity of stock bought.
        # BUY
        for trade in trades:
            utid, ticker, qty, leverage, buy_date, sell_date = trade
            df[ticker].loc[buy_date:sell_date] = qty#*leverage
            
            # Subtract the value of the trade from cash every buy
            df['cash'].loc[buy_date:] -= qty*data["Adj Close"][ticker][str(buy_date)]

        # Use price of each stock from the yfinance data and use vectorisation to multiply
        # this by the quantity of the stock we have for each time series.
        for ticker in self.tickers:
            df[ticker] *= data['Adj Close'][ticker]

        # SELL
        for trade in trades:
            utid, ticker, qty, leverage, buy_date, sell_date = trade
            # Add the value of the stock to cash on the sell date. Will appear in cash on day after.
            df['cash'].loc[sell_date+dt.timedelta(days=1):] += qty*data["Adj Close"][ticker][str(sell_date)]   

        # Add up each column to get total value column for each time series.
        for ticker in self.tickers:
            df['value'] += df[ticker]
        df['value'] += df['cash']

        # Add dataframe as an object attribute.
        self.df = df
    
    def print_dataframe(self):
        print(self.df)


# UTID:  Ticker:  Quantity:  Leverage: Buy Date:  Sell Date:
trades = [
    [1, "AAPL", 10, 1, dt.date(2013,1,2), dt.date(2013,1,4)],
    [3, "MSFT", 10, 1, dt.date(2013,1,8), dt.date(2013,1,11)],
    [4, "AAPL", 10, 1, dt.date(2013,1,8), dt.date(2013,1,14)],
    [2, "GBPUSD=X", 10, 1, dt.date(2013,1,2), dt.date(2013,1,4)]
    ]

pc = PortfolioConstructor(trades)
pc.print_dataframe()