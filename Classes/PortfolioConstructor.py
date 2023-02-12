# This class takes in list of trades (from strategy class) and displays
# the value of the portfolio at any given day (timeseries).
# Use pandas time series dataframe.

# Output will be dataframe of:
# Date:  Value:

import yfinance as yf
import pandas as pd
import datetime as dt

class PortfolioConstructor():
    def __init__(self, trades):
        super().__init__()
        self.portfolioValue = 10_000
        self.trades = trades

    def calc(self, trades):
        for trade in trades:
            utid, ticker, qty, buy_date, sell_date = trade

            buy_price, sell_price = self.get_buy_sell_prices(ticker, buy_date, sell_date)

            self.calc_pnl(qty, buy_price, sell_price)

    def get_buy_sell_prices(self, ticker, buy_date, sell_date):
        df = yf.download(ticker, buy_date, sell_date,interval="1d")
        # Assuming buying at open, and selling at close
        buy_price, sell_price = df["Open"][0], df["Close"][-1]
        return buy_price, sell_price

    def calc_pnl(self, qty, buy_price, sell_price):
        self.portfolioValue += qty*(sell_price - buy_price)

    def print_trades(self):
        print(self.trades)


# UTID:  Ticker:  Quantity:  Buy Date:  Sell Date:
trades = [
    [1, "AAPL", 10, "2020-01-02", "2020-01-03"],
    [2, "AAPL", 10, "2020-01-05", "2020-01-07"],
    [3, "AAPL", 10, "2020-01-06", "2020-01-07"],
    [4, "AAPL", 10, "2020-01-08", "2020-01-09"],
    ]

pc = PortfolioConstructor(trades=trades)
pc.calc(trades)
print(pc.portfolioValue)