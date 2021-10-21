from os import write
from psycopg2 import connect
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import pandas as pd

from timeit import default_timer as timer
import time
import math

import config
from db.database import DataBase

def initialize_alpaca_api(api_env : str) -> tradeapi.REST:
    '''
    This function initializes a connection to the Alpaca Trading API
    '''
    if api_env.lower() not in ["paper", "live"]:
        return ValueError(f"API environment ust be either paper or live")

    alpaca_api = config.API_SETTINGS["Alpaca"]
    api_settings = alpaca_api[api_env]
    return tradeapi.REST(api_settings["KEY"], alpaca_api["secret_key"], api_settings["URL"], api_version='v2')

def initialize_database() -> DataBase:
    return DataBase(config.DB_ACCESS[config.DB_LOCATION])

def populate_stocks_table(db : DataBase, symbols : list[str], time_frame : str, points : int):
    '''
    This function populates the 'stocks' table of the DB according to the provided parameters
    '''

    _allowable_time_frame = ["1Min", "5Min", "15Min", "1D", "day", "minute"]
    _max_points_per_request = 1000

    end_date = pd.Timestamp.now() - pd.Timedelta(minutes=16)
    end_date = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    if time_frame not in _allowable_time_frame:
        raise ValueError("".join([f" time_frame {time_frame} not allowed. Supported keys are \n"] +
                         [f"\t- {key} \n" for key in _allowable_time_frame]))
    
    api = initialize_alpaca_api(config.ALPACA_API_ENV)

    num_requests_required = math.ceil(points/_max_points_per_request)
    total_points_requested = points

    stock_id_dict = get_all_stocks(db)

    for symbol in symbols:

        stock_id = stock_id_dict[symbol]

        full_rv = []
        for i in range(0,num_requests_required):
            
            if i is (num_requests_required-1):
                points = total_points_requested-(i)*_max_points_per_request
            else:
                points = _max_points_per_request

            rv = api.get_barset(symbol, time_frame, end = end_date, limit = points)
            request_time = timer()

            # Get the last reported date from the response
            end_date = rv[symbol][0].t

            full_rv += rv[symbol]
            
            # Keep the pace down to avoid the rate-limit
            while (timer() - request_time) < 0.3: # 0.3 = 200 Querys / 60 Seconds (Alapca API Limit)
                time.sleep(0.25)

        # Get the corresponding stock_id
        write_values = [(f"{stock_id}", p.t, p.o , p.h, p.l, p.c, p.v) for p in full_rv]


        insert_statement = """
                                INSERT into price_minute (stock_id, date_time, open, high, low, close, volume)
                                VALUES %s
                                ON CONFLICT (stock_id, date_time) DO NOTHING
                            """
        db.execute_values(insert_statement, write_values)
        db.commit()
        print(f'Committed {len(write_values)} points to DB for {symbol}')

def get_all_stocks(db : DataBase) -> dict:
    db.execute("SELECT id, symbol from stocks")
    rv = db.cursor.fetchall()
    return {symbol : id for (id, symbol) in rv}


def create_tables(db : DataBase):

    command_list = [    
        ''' CREATE TABLE IF NOT EXISTS stocks (
            id              SERIAL                  PRIMARY KEY     , 
            symbol          TEXT                    NOT NULL UNIQUE , 
            name            TEXT                    NOT NULL        ,
            exchange        TEXT                    NOT NULL        ,
            class           TEXT                    NOT NULL        ,
            shortable       BOOLEAN                 NOT NULL        ,
            fractionable    BOOLEAN                 NOT NULL        
        )''',

        '''
            CREATE TABLE IF NOT EXISTS trading_days (
            date            DATE            PRIMARY KEY     ,
            market_open     BOOLEAN         NOT NULL        ,
            close_time      TIME                            ,
            open_time       TIME                            ,
            session_close   TIME                            ,
            session_open    TIME    
        )''',

        '''
        CREATE TABLE IF NOT EXISTS quotes_minutes (
            stock_id        INTEGER                         NOT NULL,
            date_time       TIMESTAMP WITHOUT TIME ZONE     NOT NULL,
            ask_exchange    TEXT                            NOT NULL,
            ask_price       NUMERIC                         NOT NULL,
            ask_size        NUMERIC                         NOT NULL,
            bid_exchange    TEXT                            NOT NULL,
            bid_price       NUMERIC                         NOT NULL,
            bid_size        NUMERIC                         NOT NULL,
            conditions      TEXT                            NOT NULL,
            tape            TEXT                            NOT NULL,

            PRIMARY KEY (stock_id, date_time),
            CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stocks (id)
        )''',

        '''CREATE TABLE IF NOT EXISTS price_minute ( 
            stock_id            INTEGER                             NOT NULL,
            date_time           TIMESTAMP WITHOUT TIME ZONE         NOT NULL,
            open                NUMERIC                             NOT NULL, 
            high                NUMERIC                             NOT NULL, 
            low                 NUMERIC                             NOT NULL, 
            close               NUMERIC                             NOT NULL, 
            volume              NUMERIC                             NOT NULL,

            PRIMARY KEY (stock_id, date_time),
            CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stocks (id)
        )''',

        '''CREATE INDEX ON price_minute (stock_id, date_time DESC)''',

        '''SELECT create_hypertable('price_minute', 'date_time', if_not_exists => TRUE)'''
        ]


    for command in command_list:
        db.cursor.execute(command)

    db.cursor.close()
    db.connection.commit()
    db.connection.close()

    print("Tables created")


if __name__ == "__main__":
    db = initialize_database()

    populate_stocks_table(db, ["AAPL", "TSLA"], "1Min", 2000)
    print("end")