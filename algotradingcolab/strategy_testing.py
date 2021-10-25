
from typing import Callable, Tuple

from algotradingcolab.database_management import initialize_database

import talib
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import math

'''
Develop a simple trading strategy that buys 50 shares when a stock price's 50 day SMA crosses
the 200 day SMA. Sell shares when the 50 day moving average falls below the 200 day moving average
'''


class Strategy():

    when_to_buy :  Callable = None
    when_to_sell : Callable = None
    watchlist    : list[str] = None
    workingcapital : float   = None
    max_ta_period  : int     = None
    update_technicals : Callable = None
    def __init__(self):
        pass



class BackTest():

    def __init__(self):
        self.db = initialize_database()
        self.data = {}
        pass


    def setup(self,
              date_range : Tuple[pd.Timestamp, pd.Timestamp],
              strategy : Strategy):

              self.date_range = date_range
              self.strategy = strategy

    def prepare_required_data(self):
        sql_cmd =   f"""
                        SELECT  id, symbol
                        FROM stocks
                        WHERE symbol IN {tuple(self.strategy.watchlist)}
                    """ 
 
        self.db.execute(sql_cmd)
        rv = self.db.cursor.fetchall()

        stock_id = { symbol : id for (id, symbol) in rv}

        # Build a dictionary of pandas DataFrames for each id
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        for id in stock_id.values():
            sql_cmd =   f'''
                            SELECT date_time, open, high, low, close FROM price_minute
                            WHERE stock_id = {id}
                            AND date_time > '{min(self.date_range).strftime(date_format)}'
                            AND date_time < '{max(self.date_range).strftime(date_format)}'
                        '''
                    
            self.db.execute(sql_cmd)
            rv = self.db.cursor.fetchall()

            df = { dt : [o,h,l,c] for (dt, o, h, l, c) in rv}
            df = pd.DataFrame.from_dict(df, orient="index",  columns=['o','h','l','c'], dtype="float64")
            df['avg'] = (df.o + df.c)/2
            df.sort_index(inplace = True)
            self.data[id] = df
    
    def run(self):

        self.prepare_required_data()

        self.strategy.update_technicals(self.data)
        
        for df in self.data.values():

            print(f"Earliest Data Point: {min(df.index)} \n")
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
                        # self.data[stock_id]['return'][i] = self.data[stock_id]['gain'][i]

                    else:
                        df.loc[index[i],'gain'] = (df['value'][i] - df['value'][i-1] + df['gain'][i-1]) 

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

        print("testing")
        plt.plot(df_all['total'])
        plt.show()
        

        




class MyStrat(Strategy):
    
    sma_50 : pd.DataFrame
    sma_200 : pd.DataFrame
        

    def __init__(self):
        super().__init__()
        self.watchlist = ["AAPL", "TSLA", "GE"]
        self.workingcapital = 10000



    def update_technicals(self, data : pd.DataFrame) -> None:

        for df in data.values():
            sma50 = talib.SMA(df.c, timeperiod=50)
            sma200 = talib.SMA(df.c, timeperiod=200)

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

        print("end of update_technicals()")


strat = MyStrat()
backtest = BackTest()

backtest.setup((pd.Timestamp("2021-10-12"), pd.Timestamp("2021-10-22")), strat)
backtest.run()