import yfinance as yf
import pandas as pd

aapl = yf.Ticker("aapl")
aapl_historical = aapl.history(start="2023-02-01", end="2023-02-08", interval="1d", actions=False)
print(aapl_historical)