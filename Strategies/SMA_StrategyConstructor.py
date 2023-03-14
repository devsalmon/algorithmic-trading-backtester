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

class SMA_StrategyConstructor():
	def __init__(self,start,end,ticker,period):
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

	def get_signals(self,df):
		if df['Adj Close'] > df['MA']:
			return "BUY"
		else :
			return "SELL"

	def show_trades(self):
		for trade in self.trade_order_list:
			print(trade)

#Input in Start date, End date, Ticker, and moving average period 
st = SMA_StrategyConstructor(dt.date(2019,1,1),dt.date.today(),'GLD',20)
trades = st.get_trade_order_list()
# print("trades", trades)

cons = PortfolioConstructor(trades)
# cons.print_dataframe()
# print(trades)