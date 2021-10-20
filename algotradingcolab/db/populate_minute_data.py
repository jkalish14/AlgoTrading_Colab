import timeit
from psycopg2.extras import execute_batch
from requests.models import encode_multipart_formdata
from database import DataBase
import config

import alpaca_trade_api as tradeapi
import pandas as pd
import time
from timeit import default_timer as timer


# Initialize the alpaca API
API_ENV = "Paper"
alpaca_api = config.API_SETTINGS["Alpaca"]
api_settings = alpaca_api[API_ENV]
api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')

# Get the list of tickers from the DB and conver tto a dictionary
db =DataBase(config.DB_ACCESS[config.DB_LOCATION])


def populate_for_all_stocks():
    chunk_size = 200
    start_point = timer()
    end_point = start_point

    end_date = pd.Timestamp.now() - pd.Timedelta(minutes=20)
    end_date = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    skipped_stocks = []

    for i in range(0,chunk_size*10):
        id_range = (i*chunk_size + 1, (i+1)*chunk_size + 1)
        sql_read_cmd =  f'''
                            SELECT id, symbol from stocks
                            WHERE id >= {id_range[0]}
                            AND   id < {id_range[1]}
                        '''

        db.execute(sql_read_cmd)
        rv = db.cursor.fetchall()

        ticker_dict = {id : ticker for (id, ticker) in rv}


        sql_write_cmd = '''
                            INSERT into price_minute (stock_id, date_time, open, high, low, close, volume)
                            VALUES %s
                            ON CONFLICT (stock_id, date_time) DO NOTHING
                        '''


        for (id, ticker) in ticker_dict.items():
            time.sleep(0.25)

            try:
                rv = api.get_bars(ticker, "1Min", end=end_date, limit= 1000)
                print(f"Adding {ticker} to DataBase")
                vals = [(id, str(bar.t), bar.o, bar.h, bar.l, bar.c, bar.v) for bar in rv]

                db.execute_values(sql_write_cmd, vals)
                db.commit()
                
            except Exception as error:
                print(error)
                skipped_stocks.append((id, ticker))
                print(f"Skipped Stock {(id, ticker)}")

        
        end_point = timer()
        while end_point-start_point < 60:
            time.sleep(1)
            end_point = timer()
            print("Waiting to avoid ratelimit")

    print(skipped_stocks)


def populate_for_stocks( stock_symbols : list[str]):

    end_date = pd.Timestamp.now() - pd.Timedelta(minutes=20)
    end_date = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    skipped_stocks = []

    for symbol in stock_symbols:
        sql_read_cmd =  f'''
                            SELECT id, symbol from stocks
                            WHERE symbol = '{symbol}'
                        '''

        db.execute(sql_read_cmd)
        rv = db.cursor.fetchall()

        ticker_dict = {id : ticker for (id, ticker) in rv}


        sql_write_cmd = '''
                            INSERT into price_minute (stock_id, date_time, open, high, low, close, volume)
                            VALUES %s
                            ON CONFLICT (stock_id, date_time) DO NOTHING
                        '''


        for (id, ticker) in ticker_dict.items():
            time.sleep(0.25)

            try:
                rv = api.get_bars(ticker, "1Min", end=end_date, limit= 1000)
                print(f"Adding {ticker} to DataBase")
                vals = [(id, str(bar.t), bar.o, bar.h, bar.l, bar.c, bar.v) for bar in rv]

                db.execute_values(sql_write_cmd, vals)
                db.commit()
                
            except Exception as error:
                print(error)
                skipped_stocks.append((id, ticker))
                print(f"Skipped Stock {(id, ticker)}")

if __name__ == "__main__":
    populate_for_stocks(["AAPL","TSLA","GE"])