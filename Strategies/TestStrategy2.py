import datetime as dt
from Classes.StrategyBrain import StrategyBrain
from Classes.PortfolioConstructor import PortfolioConstructor


class TestStrategy2(StrategyBrain):
    def __init__(self, start, end, ticker, MA_period):
        # Instatiates super constructor (for StrategyBrain Class)
        super().__init__(ticker, start, end)
        # Creates dataframe with indicators from StrategyBrain Class and signals from this current strategy
        self.indicators_and_signals_df = self.get_indicators(MA_period)
        self.indicators_and_signals_df["Signal"] = self.indicators_and_signals_df.apply(
            self.get_signals, axis=1
        )
        # Gets list of tuples of alternating buy and sell signals, e.g [(Buy, date), (Sell, date), (Buy...)]
        self.entry_exit_dates = self.get_entry_exit_dates(
            self.indicators_and_signals_df
        )
        # Creates 2d list of trades in format [UTID, Ticker, Quantity, Leverage, Buy Date, Sell Date]
        # for Portfolio Constructor Class
        self.trades_list = self.construct_trades_list(self.entry_exit_dates, ticker)

    def get_signals(self, df):
        # print(df)
        cond1 = df["Open"] < df["VWAP"]
        if cond1:
            return "BUY"
        else:
            return "SELL"

    def print_trades(self):
        for trade in self.trades_list:
            print(trade)


# Open         1.792700e+02
# High         1.797200e+02
# Low          1.782600e+02
# Close        1.792200e+02
# Adj Close    1.792200e+02
# Volume       6.052700e+06
# MA           1.759435e+02
# MACD         3.284501e+00
# VWAP         1.601389e+02

# Input in backtesting start date, end date, ticker, and moving average period
test_strategy_2 = TestStrategy2(dt.date(2019, 1, 1), dt.date(2023, 2, 2), "GLD", 20)
# test_strategy_2.print_trades()
test2_portfolio = PortfolioConstructor(test_strategy_2.trades_list)
test2_portfolio.print_dataframe()
