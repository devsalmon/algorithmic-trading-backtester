import datetime as dt
from Classes.StrategyBrain import StrategyBrain
from Classes.PortfolioConstructor import PortfolioConstructor
from Classes.TradeAnalysis import TradeAnalysis
from Classes.PortfolioAnalysis import PortfolioAnalysis
import pandas as pd

pd.options.display.max_rows = None


class TestStrategy4(StrategyBrain):
    def __init__(self, ticker, start, end):
        # Instatiates super constructor (for StrategyBrain Class)
        super().__init__(ticker, start, end)

        # Adds two moving average indicators to the data dataframe
        self.data["MA1"] = self.simple_moving_average(14)
        self.data["MA2"] = self.simple_moving_average(28)

        # Input my next method into the day_by_day function that itterates this method every day
        self.day_by_day(self.next)

        # Turns a list of buy and sell signals into a set of trades
        self.trades_list = self.construct_trades_list(self.entry_exit_dates, ticker)

    # This method will be run every trading day.
    def next(self, today):
        # self.stop_loss(today["Date"], 1)
        # self.take_profit(today["Date"], 1)
        if (
            self.crossover(today["Date"], "MA1", "MA2") == True
            and self.in_position == False
        ):
            self.buy(today["Date"])
        elif (
            self.crossover(today["Date"], "MA2", "MA1") == True
            and self.in_position == True
        ):
            self.sell(today["Date"])

    def get_trades(self):
        return self.trades_list
