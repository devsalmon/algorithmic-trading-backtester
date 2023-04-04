import pandas as pd 
import yfinance as yf 
import datetime as dt 
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class GraphicalConstructor:
    def __init__(self,trade_list,portfolio_df,indicator_df,main_columns):
        self.trade_list, self.portfolio_df, self.indicator_df, self.main_columns = trade_list, portfolio_df, indicator_df, main_columns

        '''Get performance of each trade, add it to each list in self.trade_list'''
        self.get_trade_performance()

        '''Construct Graphs'''
        self.construct_figure()
        self.construct_first_subplot()
        self.construct_second_subplot()
        self.construct_third_subplot()
        self.construct_fourth_subplot()
        self.miscellaneous_formatting()
        self.fig.show()

    def get_trade_performance(self):
        for trade in self.trade_list:
            df = yf.download(trade[1],trade[4],trade[5],progress=False)
            trade_performance = np.round(100*(df['Adj Close'].iloc[-1]-df['Adj Close'].iloc[0])/df['Adj Close'].iloc[0],2)
            trade.append(trade_performance)

    def construct_figure(self):
        self.fig = make_subplots(
            rows = 4,
            cols = 1,
            row_heights = [0.1,0.1,0.7,0.1],
            shared_xaxes = True,
            vertical_spacing = 0.005,
            row_titles = ['Equity','Trades','Indicators','Volume'],
            column_titles=['','','','']
            )

    def construct_first_subplot(self):
        '''Construct first subplot'''
        self.portfolio_df['Percentage Return'] = 100*(self.portfolio_df['Portfolio Value']-self.portfolio_df['Portfolio Value'].iloc[0])/self.portfolio_df['Portfolio Value'].iloc[0]
        self.fig.add_trace(
            go.Scatter(
                x=self.portfolio_df.index,
                y=self.portfolio_df['Percentage Return'],
                mode='lines',
                name='Price',
                showlegend=False
                ),
            row=1,
            col=1
            )
        self.fig.add_hline(
            y=0,
            line_dash="dot",
            row=1,
            col=1
            )
        self.fig.update_yaxes(
            ticksuffix="%",
            row=1,
            col=1
            )

    def construct_second_subplot(self):
        returns = [trade[6] for trade in self.trade_list]
        dates = [trade[5] for trade in self.trade_list]
        for count, returns in enumerate(returns):
            if returns >= 0:
                self.fig.add_trace(
                    go.Scatter(
                        x=[dates[count]],
                        y=[returns],
                        mode='markers',
                        name='Trade Returns',
                        marker=dict(
                            size=5*abs(returns)**(0.3)+2,
                            symbol='star',
                            color='green'
                            ),
                        showlegend=False
                        ),
                    row=2,
                    col=1
                    )
            elif returns < 0:
                self.fig.add_trace(
                    go.Scatter(
                        x=[dates[count]],
                        y=[returns],
                        mode='markers',
                        name='Trade Returns',
                        marker=dict(
                            size=5*abs(returns)**(0.3)+2,
                            symbol='star',
                            color='green'
                            ),
                        showlegend=False
                        ),
                    row=2,
                    col=1
                    )
            self.fig.update_yaxes(
                ticksuffix="%",
                row=2,
                col=1
                )
            self.fig.add_hline(
                y=0,
                line_dash="dot",
                row=2,
                col=1
                )

    def construct_third_subplot(self):
        for column in self.main_columns:
            self.fig.add_trace(
                go.Scatter(
                    x=self.indicator_df.index,
                    y=self.indicator_df[column],
                    mode='lines',
                    name='Price',
                    showlegend=False
                    ),
                row=3,
                col=1
                )

    def construct_fourth_subplot(self):
        self.fig.add_trace(
            go.Bar(
                x=self.indicator_df.index,
                y=self.indicator_df['Volume'],
                marker_color='red',
                showlegend=False
                ),
            row=4,
            col=1
            )
    def miscellaneous_formatting(self):
        '''Move titles to left hand side of graphs'''
        self.fig.for_each_annotation(lambda a: a.update(x = -0.055) if a.text in ['Equity','Trades','Indicators','Volume'] else())
        '''Change size of subplots'''
        self.fig.update_layout(
            height=850,
            width=1500,
            plot_bgcolor = "white"
            )
        self.fig.update_yaxes(
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='inside'
            )
        self.fig.update_xaxes(
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
            range=[list(self.indicator_df.index.date)[0],
            list(self.indicator_df.index.date)[-1]]
            )





