from TestStrategy1 import TestStrategy1
from PortfolioConstructor import PortfolioConstructor 
from TradeAnalysis import TradeAnalysis
from PortfolioAnalysis import PortfolioAnalysis
import datetime as dt


# Main pipeline:

# 1. Choose strategy with backtesting start and end dates.
test_strategy_1 = TestStrategy1(dt.date(2019, 1, 1), dt.date(2023, 2, 2), "GLD", 20)
# 2. Get the list of trades from the strategy.
trades_list = test_strategy_1.get_trades()
# 3. Create the portfolio with the list of trades from the strategy.
strategy_portfolio = PortfolioConstructor(trades_list).get_portfolio()
# 4. Calculate trade statistics and print.
trade_analysis = TradeAnalysis(trades_list)
trade_analysis.print_statistics()
# 5. Calculate portfolio statistics and print.
portfolio_analysis = PortfolioAnalysis(strategy_portfolio)
portfolio_analysis.print_statistics()
