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
        self.cash_value = 7750
        #self.portfolio_value = 10_000

        self.tickers = self.get_tickers(trades)
        # Define the columns for the df
        columns = list(self.tickers)
        columns.extend(['value', 'cash'])

        # Get portfolio start and end dates
        start_date, end_date = self.get_start_end_dates(trades)
        pandas_start_date, pandas_end_date = str(start_date).replace("-", ""), str(end_date).replace("-", "")

        # Choose date range for backtesting with periods being how many days ahead.
        date_range = pd.bdate_range(start=pandas_start_date, end=pandas_end_date)
        # Create dataframe with index as date fill in values as 0.
        df = pd.DataFrame(index=date_range, columns = columns).fillna(0)
        # Set cash column to inital portfolio cash value
        df['cash'] = self.cash_value
        data = self.get_yf_data(self.tickers, start_date, end_date)

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

    def get_tickers(self, trades):
        """Returns a list of tickers for all tickers traded in trades"""
        tickers = set()
        for trade in trades:
            utid, ticker, qty, leverage, buy_date, sell_date = trade
            if ticker not in tickers:
                tickers.add(ticker)

        return tickers

    def get_yf_data(self, tickers, start_date, end_date):
        """Returns a dataframe of tickers for the date range provided"""
        tickers = list(tickers)
        # Include line below to get rid of temporary bug of only allowing df to be
        # parsed if there are multiple tickers.
        tickers.append("AAPL")
        return yf.download(tickers, start_date, end_date, progress=False)
        
    def get_start_end_dates(self, trades):
        """Returns the start and end dates for the given trades"""
        min_start = dt.date.today()
        max_end = dt.date(1950, 1, 2)
        for trade in trades:
            start_date, end_date = trade[4], trade[5]
            if start_date < min_start:
                min_start = start_date
            if end_date > max_end:
                max_end = end_date
        return min_start, max_end + dt.timedelta(days=1)

    def print_dataframe(self):
        print(self.df)

# UTID:  Ticker:  Quantity:  Leverage: Buy Date:  Sell Date:
# trades = [
#     [1, "AAPL", 10, 1, dt.date(2013,1,2), dt.date(2013,1,4)],
#     [3, "MSFT", 10, 1, dt.date(2013,1,8), dt.date(2013,1,11)],
#     [4, "AAPL", 10, 1, dt.date(2013,1,8), dt.date(2013,1,14)],
#     [2, "GBPUSD=X", 10, 1, dt.date(2013,1,2), dt.date(2013,1,4)]
#     ]

# pc = PortfolioConstructor(trades)
# pc.print_dataframe()