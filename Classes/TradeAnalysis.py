import pandas as pd
import yfinance as yf
import datetime as dt
import numpy as np
import random as rand

# Get return list slowing down class


class TradeAnalysis:
    def __init__(self, trades: list):
        self.trades = trades
        self.main_df = self.construct_main_df()
        self.return_list = self.get_return_list()
        self.positive_return_list = [
            returns for returns in self.return_list if returns > 0
        ]
        self.negative_return_list = [
            returns for returns in self.return_list if returns <= 0
        ]

    def construct_main_df(self) -> pd.DataFrame:
        tickers = list(set([trade[1] for trade in self.trades]))
        main_df = pd.DataFrame()
        for ticker in tickers:
            main_df[ticker] = yf.download(
                ticker, dt.date(1900, 1, 1), dt.date.today(), progress=False
            )["Adj Close"]
        return main_df

    def get_data(self, ticker: str, start_date: dt, end_date: dt) -> pd.DataFrame:
        return self.main_df[ticker].loc[start_date:end_date]

    def get_longest_consecutive_wins(self) -> int:
        max_length, current_length = 0, 0
        for returns in self.return_list:
            if returns >= 0:
                current_length += 1
                if current_length > max_length:
                    max_length = current_length
            else:
                current_length = 0
        return max_length

    def get_longest_consecutive_losses(self) -> int:
        max_length, current_length = 0, 0
        for returns in self.return_list:
            if returns < 0:
                current_length += 1
                if current_length > max_length:
                    max_length = current_length
            else:
                current_length = 0
        return max_length

    def get_frequency_of_all_trades(self) -> int:
        return len(self.trades)

    def get_frequency_of_winning_trades(self) -> int:
        return len(self.positive_return_list)

    def get_frequency_of_losing_trades(self) -> int:
        return len(self.negative_return_list)

    def get_average_length(self) -> float:
        length_list = []
        for trade in self.trades:
            length_list.append((trade[5] - trade[4]).days)
        average_length = np.mean(length_list)
        return round(average_length, 2)

    def get_average_winning_length(self) -> float:
        length_list = []
        for count, returns in enumerate(self.return_list):
            if returns > 0:
                days = (self.trades[count][5] - self.trades[count][4]).days
                length_list.append(days)
        average_length = np.mean(length_list)
        return round(average_length, 2)

    def get_average_losing_length(self) -> float:
        length_list = []
        for count, returns in enumerate(self.return_list):
            if returns <= 0:
                days = (self.trades[count][5] - self.trades[count][4]).days
                length_list.append(days)
        average_length = np.mean(length_list)
        return round(average_length, 2)

    def get_return_list(self) -> list:
        return_list = []
        for trade in self.trades:
            utid, ticker, qty, leverage, buy_date, sell_date = trade
            df = self.get_data(ticker,buy_date,sell_date) 
            trade_return = 100 * ((df.iloc[-1] / df.iloc[0]) - 1)
            return_list.append(trade_return)
        return return_list

    def get_average_returns(self) -> float:
        average_returns = np.mean(self.return_list)
        return round(average_returns, 2)

    def get_win_rate(self) -> float:
        win_rate = 100 * (len(self.positive_return_list) / len(self.return_list))
        return round(win_rate, 2)

    def get_loss_rate(self) -> float:
        loss_rate = 100 - self.get_win_rate()
        return loss_rate

    def get_average_win_returns(self) -> float:
        average_win_returns = np.mean(self.positive_return_list)
        return round(average_win_returns, 2)

    def get_average_loss_return(self) -> float:
        average_loss_returns = np.mean(self.negative_return_list)
        return round(average_loss_returns, 2)

    def get_best_winning_trade(self) -> float:
        return np.round(np.max(self.positive_return_list))

    def get_worst_winning_trade(self) -> float:
        return np.round(np.min(self.positive_return_list), 2)

    def get_best_losing_trade(self) -> float:
        return np.round(np.max(self.negative_return_list))

    def get_worst_losing_trade(self) -> float:
        return np.round(np.min(self.negative_return_list), 2)

    def format_column(self, input_one: any, input_two: any) -> None:
        input_one, input_two = str(input_one), str(input_two)
        while len(input_one) != 30:
            input_one += " "
        while len(input_two) != 15:
            input_two += " "
        print(input_one, input_two)

    def show_trades(self) -> None:
        for trade in self.trades:
            print(trade)

    def print_statistics(self) -> None:
        self.format_column("All Trades", "Portfolio")
        print("-----------------------------------------")
        self.format_column("Frequency", f"{self.get_frequency_of_all_trades()}")
        self.format_column("Average Length", f"{self.get_average_length()} Days")
        self.format_column("Average Returns", f"{self.get_average_returns()} %")
        print("-----------------------------------------")
        self.format_column("Winning Trades", "")
        self.format_column("Frequency", f"{self.get_frequency_of_winning_trades()}")
        self.format_column(
            "Average Length", f"{self.get_average_winning_length()} Days"
        )
        self.format_column("Win Rate", f"{self.get_win_rate()} %")
        self.format_column("Average Win Return", f"{self.get_average_win_returns()} %")
        self.format_column("Best Trade", f"{self.get_best_winning_trade()} %")
        self.format_column("Worst Trade", f"{self.get_worst_winning_trade()} %")
        self.format_column('Longest Win Steak',f'{self.get_longest_consecutive_wins()}')
        print("-----------------------------------------")
        self.format_column("Losing Trades", "")
        self.format_column("Frequency", f"{self.get_frequency_of_losing_trades()}")
        self.format_column("Average Length", f"{self.get_average_losing_length()} Days")
        self.format_column("Loss Rate", f"{self.get_loss_rate()} %")
        self.format_column("Average Loss Return", f"{self.get_average_loss_return()} %")
        self.format_column("Best Trade", f"{self.get_best_losing_trade()} %")
        self.format_column("Worst Trade", f"{self.get_worst_losing_trade()} %")
        self.format_column('Longest Loss Streak',f'{self.get_longest_consecutive_losses()}')
        print("-----------------------------------------")


# Input in Start date, End date, Ticker, and moving average period
# st = SMA_StrategyConstructor(dt.date(2004,1,1),dt.date.today(),'GLD',20)
# trades = st.get_trade_order_list()

# Enter in trade analysis
# ta = TradeAnalysis(trades)
# ta.show_statistics()
