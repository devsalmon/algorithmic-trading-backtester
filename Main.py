from Strategies.TestStrategy3 import TestStrategy3
from Classes.PortfolioConstructor import PortfolioConstructor
from Classes.TradeAnalysis import TradeAnalysis
from Classes.PortfolioAnalysis import PortfolioAnalysis
import datetime as dt


# Main pipeline:

# 1. Choose strategy with backtesting start and end dates.
test_strategy_3 = TestStrategy3('GLD',dt.date(2018,1,1),dt.date(2020,1,3))
# 2. Get the list of trades from the strategy.
trades_list = test_strategy_3.get_trades()
# 3. Create the portfolio with the list of trades from the strategy.
strategy_portfolio = PortfolioConstructor(trades_list).get_portfolio()
# 4. Calculate trade statistics and print.
trade_analysis = TradeAnalysis(trades_list)
trade_analysis.print_statistics()
# 5. Calculate portfolio statistics and print.
portfolio_analysis = PortfolioAnalysis(strategy_portfolio)
portfolio_analysis.print_statistics()



