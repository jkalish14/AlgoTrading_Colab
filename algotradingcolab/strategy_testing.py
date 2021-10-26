
from re import template
from typing import Callable, Tuple

from algotradingcolab.database_management import initialize_database

import talib
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import math

import threading

'''
Develop a simple trading strategy that buys 50 shares when a stock price's 50 day SMA crosses
the 200 day SMA. Sell shares when the 50 day moving average falls below the 200 day moving average
'''

class Strategy():

    watchlist               : list[str] = None
    workingcapital          : float     = None
    max_ta_period           : int       = None
    determine_when_to_trade : Callable  = None
    benchmark               : list[str] = None

class BackTest():

    def __init__(self):
        self.db = initialize_database()
        self.data = {}
        self.stock_id = {}

    def setup(self,
              date_range : Tuple[pd.Timestamp, pd.Timestamp],
              strategy : Strategy):

              self.date_range = date_range
              self.strategy = strategy 


    def prepare_required_data(self):
        sql_cmd =   f"""
                        SELECT  id, symbol
                        FROM stocks
                        WHERE symbol IN {tuple(self.strategy.watchlist) + tuple(self.strategy.benchmark)}
                    """ 
 
        self.db.execute(sql_cmd)
        rv = self.db.cursor.fetchall()

        self.stock_id = { symbol : id for (id, symbol) in rv}

        # Build a dictionary of pandas DataFrames for each id
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        for id in self.stock_id.values():
            sql_cmd =   f'''
                            SELECT date_time, open, close FROM price_minute
                            WHERE stock_id = {id}
                            AND date_time > '{min(self.date_range).strftime(date_format)}'
                            AND date_time < '{max(self.date_range).strftime(date_format)}'
                            ORDER BY date_time DESC
                        '''
                    
            self.db.execute(sql_cmd)
            rv = self.db.cursor.fetchall()

            df = { dt : [o,c] for (dt, o, c) in rv}
            df = pd.DataFrame.from_dict(df, orient="index",  columns=['o','c'], dtype="float64")
            df['avg'] = (df.o + df.c)/2
            df.sort_index(inplace = True)

            if id == self.stock_id[self.strategy.benchmark[0]]:
                self.benchmark_data = df
            else:
                self.data[id] = df
        
    @staticmethod
    def iterate_over_stock(symbol : str, df : pd.DataFrame):
        print(f"Earliest Data Point for {symbol}: {min(df.index)} \n")
        df.loc[:,'holding'] = 0
        df.loc[:,'value'] = 0
        df.loc[:,'gain'] = 0
        # self.data[stock_id]['return'] = 0 
        index = df.index

        for i in range(0,len(df)):
            move = df['move'][i]

            if i == 0 and move == 0:
                df.loc[index[i],'holding']= 0
                df.loc[index[i],'value'] = 0
                df.loc[index[i],'gain'] = 0


            elif i == 0 and move != 0:
                df.loc[index[i],'holding'] = move
                df.loc[index[i],'value'] = move * (df[i].avg)
                df.loc[index[i],'gain'] = 0

            else:
                df.loc[index[i],'holding'] = df['holding'][i-1] + move 
                df.loc[index[i],'value'] = df['holding'][i] * (df.avg[i])

                if move > 0:
                    df.loc[index[i],'gain'] = 0 + df['gain'][i-1]

                elif move < 0:
                    df.loc[index[i],'gain'] = (abs(move)* (df.avg[i]) - df['value'][i-1]) + df['gain'][i-1]

                else:
                    df.loc[index[i],'gain'] = (df['value'][i] - df['value'][i-1] + df['gain'][i-1]) 

        print(f"Done with {symbol}!")


    def run(self):

        self.prepare_required_data()

        self.strategy.determine_when_to_trade(self.data)
        
        # Start a thread for each of the stocks and wait for them all to finish
        threads = [WorkerThread(self,stock_id, df) for (stock_id, df) in self.data.items()]
        [t.start() for t in threads]
        [t.join() for t in threads]

        # Merge all the results into a single dataframe and calculate the cumulative return
        current_time = min(self.date_range)
        end_time = max(self.date_range)
        periods = math.ceil((end_time-current_time).total_seconds() / 60)
        all_periods = [current_time + pd.Timedelta(minutes=1*i) for i in range(0,periods)]
        df_all = pd.DataFrame(index=all_periods)    
        
        [df_all := df_all.join(df['gain'], rsuffix=stock_id) for (stock_id, df) in self.data.items()]
        
        for header in df_all.columns:
            df_all.loc[:,header] = pd.to_numeric(df_all[header])

        df_all = df_all.interpolate(method="linear", axis=0)
        df_all = df_all.fillna(0)
        df_all.loc[:,'total'] = df_all.sum(axis=1)


        ## PLOT THE PERFORMANCE

        # split data into chunks where averages cross each other
        df_all['label'] = np.where(df_all['total']> 0, 1, 0)
        df_all['group'] = df_all['label'].ne(df_all['label'].shift()).cumsum()
        df_all = df_all.groupby('group')
        dfs = []
        for name, data in df_all:
            dfs.append(data)

        # custom function to set fill color
        def fillcol(label):
            if label >= 1:
                return 'rgba(0,250,0,0.4)'
            else:
                return 'rgba(250,0,0,0.4)'

        fig = go.Figure()

        for df in dfs:
            fig.add_traces(go.Scatter(x=df.index, y = df['total'],
                                    line = dict(color='rgba(0,0,0,0)'),
                                    showlegend = False))
            
            fig.add_traces(go.Scatter(x=df.index, y = df['total'] * 0,
                                    line = dict(color='rgba(0,0,0,0)'),
                                    fill='tonexty', 
                                    hoverinfo="skip",
                                    fillcolor = fillcol(df['label'].iloc[0]),
                                    showlegend=False))


        # fig.add_trace(go.Scatter(x=df_all.index, y = df_all['total'], line_color='forestgreen'))
        fig.update_layout(
            template = 'plotly_dark',
            hovermode='x unified'
        )

        fig.update_yaxes(title="Portfolio Return $")
        fig.update_xaxes(title="Date")
        fig.show()

        
class MyStrat(Strategy):


    def __init__(self):
        super().__init__()
        self.watchlist = ['AAPL','TSLA','GE', 'MSFT', 'SQ']
        self.benchmark = ['SPY']
        self.workingcapital = 10000

    def determine_when_to_trade(self, data : pd.DataFrame) -> None:

        for df in data.values():
            sma50 = talib.SMA(df.c, timeperiod=50)
            sma200 = talib.SMA(df.c, timeperiod=200)

            df.loc[:,"signal"] = sma50-sma200
            # Determine the signal and append the move to the df
            zero_crossings = np.sign(sma50-sma200)
            zero_crossings = zero_crossings.fillna(0)
            zero_crossings = zero_crossings.diff()

            negative_going_zero_crossings = (zero_crossings > 0) # indicates buy
            positive_going_zero_crossings = (zero_crossings < 0) # indicates sell
            
            # Make sure a buy occurs before a sell
            first_pgz_index = positive_going_zero_crossings[positive_going_zero_crossings == True].index[0]
            first_ngz_index = negative_going_zero_crossings[negative_going_zero_crossings == True].index[0]
            if first_pgz_index < first_ngz_index:
                positive_going_zero_crossings.loc[first_pgz_index] =  False 

            df.loc[:,'move'] = 0
            df.loc[negative_going_zero_crossings,'move'] = 50    # Number of shares to buy
            df.loc[positive_going_zero_crossings,'move'] = -50   # number od shares to sell


class WorkerThread(threading.Thread):
    def __init__(self, symbol : str,  back_test_obj : BackTest, df : pd.DataFrame):
        super().__init__()
        self.back_test = back_test_obj
        self.df = df
        self.symbol = symbol

    def run(self):
        BackTest.iterate_over_stock(symbol = self.symbol, df = self.df)


strat = MyStrat()
backtest = BackTest()

backtest.setup((pd.Timestamp("2021-9-20"), pd.Timestamp("2021-10-22")), strat)
backtest.run()