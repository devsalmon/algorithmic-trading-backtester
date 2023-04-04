import yfinance as yf
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import typing


class StrategyBrain:
    def __init__(self, ticker: str, start_date: dt, end_date: dt):
        # super().__init__()
        self.backtest_start_date = start_date
        self.backtest_end_date = end_date
        self.in_position = False
        self.entry_exit_dates = []
        self.last_entry_price = -1
        self.ticker = ticker

        # Columns - Open, High, Low, Close, Adj Close, Volume
        self.data = yf.download(ticker, start_date, end_date, progress=False)

    """Function that takes in two columns in self.df and returns True/False in the case of a crossover"""

    def crossover(
        self, date: dt, column_one: pd.DataFrame, column_two: pd.DataFrame
    ) -> bool:
        # Check for the position of the date in self.df
        position = list(self.data.index.date).index(date)

        """Return a False on the first row"""
        if position == 0:
            return False
        elif position != 0:
            """Get the price of first and second column on the given date and the day before"""
            first_column_today, first_column_yeserday = (
                self.data[column_one].iloc[position],
                self.data[column_one].iloc[position - 1],
            )
            second_column_today, second_column_yesterday = (
                self.data[column_two].iloc[position],
                self.data[column_two].iloc[position - 1],
            )

            """Check for crossover and return True in the case of a crossover"""
            if (
                first_column_today > second_column_today
                and first_column_yeserday < second_column_yesterday
            ):
                return True

    # Loop through each day of trading, applying the next function each day
    def day_by_day(self, func) -> None:
        every_day_dict = self.data.reset_index().to_dict(orient="records")
        for day_data in every_day_dict:
            func(day_data)
        self.check_for_stub_period()

    # Check if the last trade has been closed, if it hasn't a final sell signal is appended
    # TODO (fix issue where trade can be closed on a weekend)
    def check_for_stub_period(self) -> None:
        if self.entry_exit_dates[-1][0] == "Buy":
            self.entry_exit_dates.append(
                ("Sell", pd.Timestamp(self.backtest_end_date, tz=None).date())
            )

    # Appends a buy signal to entry_exit_dates with a tuple ('Sell',date)
    def buy(self, date: dt) -> None:
        self.entry_exit_dates.append(("Buy", date.date()))
        self.last_entry_price = self.data.loc[date, "Adj Close"]
        self.in_position = True

    # Appends a sell signal to exit entry dates with a tuple ('Sell',date)
    def sell(self, date: dt) -> None:
        self.in_position = False
        self.entry_exit_dates.append(("Sell", date.date()))

    def stop_loss(self, date: dt, limit_percentage: float) -> None:
        if self.in_position:
            current_close = self.data.loc[date, "Adj Close"]
            drawdown = (
                (self.last_entry_price - current_close) / self.last_entry_price
            ) * 100
            if drawdown > limit_percentage:
                self.sell(date)

    def take_profit(self, date: dt, take_profit_percentage: float) -> None:
        if self.in_position:
            current_close = self.data.loc[date, "Adj Close"]
            rise = (
                (current_close - self.last_entry_price) / self.last_entry_price
            ) * 100
            if rise > take_profit_percentage:
                self.sell(date)

    # Creates dataframe with columns for all indecators.
    def get_indicators(self, MA_period: int) -> pd.DataFrame:
        # self.data.drop(["Open", "High", "Low", "Close", "Volume"], axis=1, inplace=True)
        self.data["MA"] = self.simple_moving_average(MA_period)
        self.data["MACD"] = self.macd()
        self.data["VWAP"] = self.vwap()
        # TODO all indicators here...
        return self.data

    # Gets list of tuples of alternating buy and sell signals, e.g [(Buy, date), (Sell, date), (Buy...)]
    def get_entry_exit_dates(self, indicators_and_signals_df: pd.DataFrame) -> list:
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
            entry_exit_dates.append(
                ("SELL", pd.Timestamp(self.backtest_end_date, tz=None))
            )
        return entry_exit_dates

    # Creates 2d list of trades in format [UTID, Ticker, Quantity, Leverage, Buy Date, Sell Date]
    # for Portfolio Constructor Class
    def construct_trades_list(self, entry_exit_dates, ticker) -> list:
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

    # def next, buy and sell

    def simple_moving_average(self, period: int) -> pd.DataFrame:
        """
        Returns the SMA for the given period

        [https://en.wikipedia.org/wiki/Moving_average#Simple_moving_average]
        """
        return self.data.rolling(window=period).mean()["Adj Close"]

    def exponential_moving_average(self, period: int) -> pd.DataFrame:
        """
        Returns the EMA (giving more weight to newer data) for the given period

        [https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average]
        """
        return self.data.ewm(span=period).mean()["Adj Close"]

    def macd(self) -> pd.DataFrame:
        """
        Returns the MACD (Moving Average Convergence / Divergence)for periods of 12 and 26

        [https://en.wikipedia.org/wiki/MACD]
        """
        return self.exponential_moving_average(12) - self.exponential_moving_average(26)

    def macd_signal_line(self) -> pd.DataFrame:
        """Returns the signal line for the MACD which is an EMA of period 9"""
        return self.exponential_moving_average(9)

    def macd_histogram(self) -> pd.DataFrame:
        """Returns the histogram for MACD"""
        return self.macd() - self.macd_signal_line()

    def bollinger_bands(self, period: int, numsd: int) -> pd.DataFrame:
        """
        Returns the average, upper and lower bands for Bollinger Bands

        [https://en.wikipedia.org/wiki/Bollinger_Bands]
        """
        df = pd.DataFrame()
        df["Average"] = self.data.rolling(window=period)["Adj Close"].mean()
        standard_deviation = self.data.rolling(window=period)["Adj Close"].std()
        df["Upper Band"] = df["Average"] + (standard_deviation * numsd)
        df["Lower Band"] = df["Average"] - (standard_deviation * numsd)

        return df

    def get_max_high_price(self) -> float:
        """Returns the max high price"""
        return np.round(self.data["High"].max(), 2)

    def get_min_low_price(self) -> float:
        """Returns the min low price"""
        return np.round(self.data["Low"].min(), 2)

    def get_max_close_price(self) -> float:
        """Returns the max close price"""
        return np.round(self.data["Adj Close"].max(), 2)

    def get_min_close_price(self) -> float:
        """Returns the min close price"""
        return np.round(self.data["Adj Close"].min(), 2)

    def vwap(self) -> pd.DataFrame:
        """
        Returns Volume Weighted Average Price (VWAP)

        [https://en.wikipedia.org/wiki/Volume-weighted_average_price]

        """
        df = pd.DataFrame()
        # Calculate Typical Price
        df["TP"] = (self.data["Low"] + self.data["High"] + self.data["Close"]) / 3
        df["VWAP"] = (df["TP"] * self.data["Volume"]).cumsum() / self.data[
            "Volume"
        ].cumsum()

        return df["VWAP"]

    def rsi(self, period: int = 14) -> pd.DataFrame:
        """
        Returns the Relative Strength Index using EMA with a default period of 14

        [https://en.wikipedia.org/wiki/Relative_strength_index]

        """
        df = pd.DataFrame()
        change = self.data["Adj Close"].diff()

        # Clip for days with positive price change
        up = change.clip(lower=0)

        # Clip for days with negative price change (* -1 to make it all positive for division purposes)
        down = -change.clip(upper=0)

        # Get moving averages for up and down data
        df["ma_up"] = up.ewm(span=period - 1, adjust=True, min_periods=period).mean()
        df["ma_down"] = down.ewm(
            span=period - 1, adjust=True, min_periods=period
        ).mean()

        rsi = df["ma_up"] / df["ma_down"]
        df["RSI"] = 100 - (100 / (1 + rsi))

        return df["RSI"]

    def mfi(self, period: int = 14) -> pd.DataFrame:
        """
        Returns the Money Flow Index with a default period of 14

        [https://en.wikipedia.org/wiki/Money_flow_index]

        MFI = 100 - (100 / (1 + money ratio))

        where
            money ratio = positive money flow / negative money flow
            positive money flow = added money flow of all days where typical price (TP) is higher than previous day's TP
            negative money flow = added money flow of all days where typical price (TP) is lower than previous day's TP
        """
        df = pd.DataFrame()
        # Calculate Typical Price
        df["TP"] = (self.data["Low"] + self.data["High"] + self.data["Close"]) / 3
        # Calculate Raw Money Flow
        df["RMF"] = df["TP"] * self.data["Volume"]
        # Calculate Money Flow Ratio where PMF = Positive Money Flow, NMF = Negative Money Flow

        # Calculate the change in typical price from the previous day
        df["change"] = df["TP"].diff()

        # Calculate the number of days that have a positive and negative change
        df["1PMF"] = df["RMF"].where(df["change"] >= 0).fillna(0)
        df["1NMF"] = df["RMF"].where(df["change"] < 0).fillna(0)

        df["14PMF"] = df["1PMF"].rolling(window=period).sum()
        df["14NMF"] = df["1NMF"].rolling(window=period).sum()

        df["Money Ratio"] = df["14PMF"] / df["14NMF"]

        # Calculate MFI
        df["MFI"] = 100 - (100 / (1 + df["Money Ratio"]))
        return df["MFI"]

    def up_days(self) -> int:
        """
        Returns true if the day has a positive change from the previous day, otherwise false
        """
        change = self.data["Close"].diff()
        return change > 0

    def is_up_day(self, date: dt) -> bool:
        """
        Returns if the specified day had a positive change
        """
        change = self.data["Close"].diff()
        return change.loc[str(date)] > 0
