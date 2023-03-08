import backtrader as bt
import yfinance as yf
import pandas as pd
import datetime as dt
import numpy as np

dataframe = yf.download('AAPL', start='2020-01-01')
print(dataframe)

cerebro = bt.Cerebro()
feed = bt.feeds.PandasData(dataname=dataframe)
cerebro.adddata(feed)
# Create a subclass of Strategy to define the indicators and logic

class SmaCross(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=10,  # period for the fast moving average
        pslow=30   # period for the slow moving average
    )

    def __init__(self):
        sma1 = bt.ind.SMA(period=self.p.pfast)  # fast moving average
        sma2 = bt.ind.SMA(period=self.p.pslow)  # slow moving average
        self.crossover = bt.ind.CrossOver(sma1, sma2)  # crossover signal

    def next(self):
        if not self.position:  # not in the market
            if self.crossover > 0:  # if fast crosses slow to the upside
                self.buy()  # enter long

        elif self.crossover < 0:  # in the market & cross to the downside
            self.close()  # close long position

cerebro.addstrategy(SmaCross)  # Add the trading strategy

cerebro.addsizer(bt.sizers.PercentSizer, percents=50) # Uses 50% of portfolio in trade

cerebro.broker.setcommission(commission=0.005)

cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="annualReturn")

test = cerebro.run()  # run it all
cerebro.plot()  # and plot it with a single command

print(test[0].analyzers.annualReturn.get_analysis())