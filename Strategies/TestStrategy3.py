import datetime as dt
from Classes.StrategyBrain import StrategyBrain
from Classes.PortfolioConstructor import PortfolioConstructor
from Classes.TradeAnalysis import TradeAnalysis
from Classes.PortfolioAnalysis import PortfolioAnalysis
import pandas as pd
pd.options.display.max_rows = None


class TestStrategy3(StrategyBrain):
    def __init__(self,ticker,start,end):
    	# Instatiates super constructor (for StrategyBrain Class)
         super().__init__(ticker, start, end)

         #Adds two moving average indicators to the data dataframe
         self.data['MA1'] = self.simple_moving_average(14)
         self.data['MA2'] = self.simple_moving_average(28)

         #Input my next method into the day_by_day function that itterates this method every day
         self.day_by_day(self.next)

         #Turns a list of buy and sell signals into a set of trades
         self.trades_list = self.construct_trades_list(self.entry_exit_dates, ticker)

    #This method will be run every trading day. 
    def next(self,today):
        if today['MA1'] > today['MA2'] and self.in_position == False:
            self.buy(today['Date'])
        elif today['MA1'] <= today['MA2'] and self.in_position == True:
            self.sell(today['Date'])

    def get_trades(self):
        return self.trades_list




