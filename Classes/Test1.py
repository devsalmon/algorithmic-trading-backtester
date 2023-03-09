import datetime as dt
from StrategyBrain import StrategyBrain
from PortfolioConstructor import PortfolioConstructor


class Test1(StrategyBrain):
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
        if df["Adj Close"] > df["MA"]:
            return "BUY"
        else:
            return "SELL"

    def print_trades(self):
        for trade in self.trades_list:
            print(trade)


# Input in backtesting start date, end date, ticker, and moving average period
test1_strategy = Test1(dt.date(2019, 1, 1), dt.date(2023, 2, 2), "GLD", 20)
test1_portfolio = PortfolioConstructor(test1_strategy.trades_list)
test1_portfolio.print_dataframe()