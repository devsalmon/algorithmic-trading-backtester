import yfinance as yf
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt


class StrategyBrain:
    def __init__(self, ticker, start_date, end_date):
        # super().__init__()
        self.backtest_start_date = start_date
        self.backtest_end_date = end_date

        # Columns - Open, High, Low, Close, Adj Close, Volume
        self.data = yf.download(ticker, start_date, end_date, progress=False)

    # Creates dataframe with columns for all indecators.
    def get_indicators(self, MA_period):
        self.data.drop(["Open", "High", "Low", "Close", "Volume"], axis=1, inplace=True)
        self.data["MA"] = self.simpleMovingAverage(MA_period)
        # TODO all indicators here...
        return self.data

    # Gets list of tuples of alternating buy and sell signals, e.g [(Buy, date), (Sell, date), (Buy...)]
    def get_entry_exit_dates(self, indicators_and_signals_df):
        entry_exit_dates = []
        signal_list = list(indicators_and_signals_df["Signal"])
        dates_list = list(indicators_and_signals_df.index)
        # Loops through signals and records date at which there is a switch in signal.
        for i, date in enumerate(dates_list):
            # Make sure first action is a BUY.
            if not entry_exit_dates:
                if signal_list[i] == "BUY":
                    entry_exit_dates.append([signal_list[i], date])
            # On first occurence of a buy or sell (after the first buy), execute that signal.
            elif signal_list[i] != signal_list[i - 1]:
                entry_exit_dates.append([signal_list[i], date])
        # Sell assets on last day if last signal was BUY.
        if entry_exit_dates[-1][0] == "BUY":
            entry_exit_dates.append(("SELL", self.backtest_end_date))
        return entry_exit_dates

    # Creates 2d list of trades in format [UTID, Ticker, Quantity, Leverage, Buy Date, Sell Date]
    # for Portfolio Constructor Class
    def construct_trades_list(self, entry_exit_dates, ticker):
        trades_list = []
        number_of_trades = len(entry_exit_dates)
        # Step = 2 as the list of entry_exit_dates alternates between buy and sell.
        for i in range(0, number_of_trades, 2):
            # [UTID, Ticker, Quantity, Leverage, Buy Date, Sell Date]
            trades_list.append(
                [
                    i // 2,
                    ticker,
                    100,
                    1,
                    entry_exit_dates[i][1],
                    entry_exit_dates[i + 1][1],
                ]
            )
        return trades_list

    def simpleMovingAverage(self, period):
        """Returns the SMA for the given period"""
        return self.data.rolling(window=period).mean()["Adj Close"]

    def exponentialMovingAverage(self, period):
        """Returns the EMA (giving more weight to newer data) for the given period"""
        return self.data.ewm(span=period).mean()["Adj Close"]

    def macd(self):
        """Returns the MACD (MA convergence divergence) for periods of 12 and 26"""
        return self.exponentialMovingAverage(12) - self.exponentialMovingAverage(26)

    def macd_signalLine(self):
        """Returns the signal line for the MACD which is an EMA of period 9"""
        return self.exponentialMovingAverage(9)

    def macd_histogram(self):
        """Returns the histogram for MACD"""
        return self.macd() - self.macd_signalLine()

    def bollingerBands(self, period, numsd):
        """Returns the average, upper and lower bands for Bollinger Bands"""
        df = pd.DataFrame()
        df["Average"] = self.data.rolling(window=period)["Adj Close"].mean()
        standard_deviation = self.data.rolling(window=period)["Adj Close"].std()
        df["Upper Band"] = df["Average"] + (standard_deviation * numsd)
        df["Lower Band"] = df["Average"] - (standard_deviation * numsd)

        return df

    def get_max_high_price(self):
        """Returns the max high price"""
        return np.round(self.data["High"].max(), 2)

    def get_min_low_price(self):
        """Returns the min low price"""
        return np.round(self.data["Low"].min(), 2)

    def get_max_close_price(self):
        """Returns the max close price"""
        return np.round(self.data["Adj Close"].max(), 2)

    def get_min_close_price(self):
        """Returns the max close price"""
        return np.round(self.data["Adj Close"].min(), 2)

    def vwap(self):
        """Returns Volume Weighted Average Price"""
        df = pd.DataFrame()
        # Calculate Typical Price
        df["TP"] = (self.data["Low"] + self.data["High"] + self.data["Close"]) / 3
        df["VWAP"] = (df["TP"] * self.data["Volume"]).cumsum() / self.data[
            "Volume"
        ].cumsum()

        return df["VWAP"]

    def up_days(self):
        """Returns true if the day has a +ve change from the previous day, otherwise false"""
        change = self.data["Close"].diff()
        return change > 0

    def is_up_day(self, date):
        """Returns if the specified day has a positive change"""
        change = self.data["Close"].diff()
        return change.loc[str(date)] > 0


# if __name__ == '__main__':
#     s = Strategy("AAPL", dt.date(2023,1,1), dt.date.today(), '1d')
#     plt.plot(s.data["Open"])
#     print(s.is_up_day(dt.date(2023, 3, 7)))

#     plt.plot(s.vwap())
#     plt.show()
