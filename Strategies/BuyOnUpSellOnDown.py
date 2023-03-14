import datetime as dt
import pandas as pd
import numpy as np
# From filename import classname
# TODO NEED TO IMPORT FROM PARENT FOLDER
from Strategy import Strategy

# The strategy will be code which we will get to later, however, what
# it will output is an dataframe of:

# UTID:  Ticker:  Quantity:  Buy Date:  Sell Date:

# class Strategy():
#     def __init__(self):
#         super().__init__()

import yfinance as yf 
import datetime as dt 
import pandas as pd 

from PortfolioConstructor import PortfolioConstructor

class BuyOnUpSellOnDown(Strategy):
	def __init__(self, ticker, start, end, period):
		Strategy.__init__(self, ticker, start, end, '1d')
		self.start_date = start 
		self.end_date = end
		self.ticker = ticker
		self.period = period
		self.df = self.get_df()
		self.entry_exit_dates = self.get_exit_entry_dates()
		self.trade_order_list = self.get_trade_order_list()

	def get_df(self):
		df = yf.download(self.ticker,self.start_date,self.end_date,progress=False)
		df.drop(['Open','High','Low','Close','Volume'],axis=1,inplace=True)
		df['MA'] = df['Adj Close'].rolling(window=self.period).mean()
		df['Signal'] = df.apply(self.get_signals, axis=1)
		return df

	def get_exit_entry_dates(self):
		entry_exit_dates = []
		signal_list = list(self.df['Signal'])
		for count,date in enumerate(list(self.df.index)):
			if count != 0:
				#Check for buy or sell rating
				if signal_list[count-1] == 'SELL' and signal_list[count] == 'BUY':
					entry_exit_dates.append(("ENTRY",date))
				elif signal_list[count-1]== "BUY" and signal_list[count] == "SELL":
					entry_exit_dates.append(("EXIT",date))
		return entry_exit_dates

	def get_trade_order_list(self):
		# TODO - add in lot sizing
		trade_order_list = []
		count = 0
		if self.entry_exit_dates[-1][0] == "ENTRY":
			self.entry_exit_dates.append(("EXIT",dt.date.today()))
		for i in range(int(len(self.entry_exit_dates)*0.5)):
			entry_date = self.entry_exit_dates[2*i][1]
			exit_date = self.entry_exit_dates[2*i+1][1]
			count += 1
			trade_order_list.append([count,self.ticker,100,1,entry_date.date(),exit_date.date()])
		return trade_order_list

	def get_signals(self, df):
		if self.is_up_day(str(df.name)[:-9]):
			return "BUY"
		else :
			return "SELL"

	def show_trades(self):
		for trade in self.trade_order_list:
			print(trade)

#Input in Start date, End date, Ticker, and moving average period 
st = BuyOnUpSellOnDown("AAPL", dt.date(2019,1,1),dt.date.today(),20)
trades = st.get_trade_order_list()

cons = PortfolioConstructor(trades)
cons.print_dataframe()
# print(trades)