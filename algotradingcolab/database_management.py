from datetime import date, timedelta
from typing import Union
import alpaca_trade_api as tradeapi
import pandas as pd

from timeit import default_timer as timer
import time
import math

from psycopg2.extras import execute_batch

from algotradingcolab import config
from algotradingcolab.database import DataBase

def initialize_alpaca_api(api_env : str) -> tradeapi.REST:
    '''
    This function initializes a connection to the Alpaca Trading API
    '''
    if api_env.lower() not in ["paper", "live"]:
        return ValueError(f"API environment ust be either paper or live")

    alpaca_api = config.API_SETTINGS["Alpaca"][api_env]
    return tradeapi.REST(alpaca_api["public_key"], alpaca_api["secret_key"], alpaca_api["URL"], api_version='v2')

def initialize_database() -> DataBase:
    return DataBase(config.DB_ACCESS[config.DB_LOCATION])

def populate_price_table(db         : DataBase,
                         symbols    : Union[str, list[str]],
                         time_frame : str,
                         points     : int):
    '''
    This function populates the 'stocks' table of the DB according to the provided parameters
    '''

    _allowable_time_frame = ["1Min", "5Min", "15Min", "1D", "day", "minute"]
    _table_mapping = {"1Min" : "price_minute", "5Min" : None, "15Min" : None, "1D" : "price_day", "day" : "price_day", "minute" : None} 
    _max_points_per_request = 1000


    if time_frame not in _allowable_time_frame:
        raise ValueError("".join([f" time_frame {time_frame} not allowed. Supported keys are \n"] +
                         [f"\t- {key} \n" for key in _allowable_time_frame]))
    
    api = initialize_alpaca_api(config.ALPACA_API_ENV)

    num_requests_required = math.ceil(points/_max_points_per_request)
    total_points_requested = points

    stock_id_dict = get_all_stock_symbols(db)

    if isinstance(symbols, str):
        symbols = [symbols]
    
    error_on = []
    for symbol in symbols:

        end_date = pd.Timestamp.now(tz='America/New_York') - pd.Timedelta(minutes=16)

        stock_id = stock_id_dict[symbol]

        full_rv = []
        for i in range(0,num_requests_required):
            
            if i is (num_requests_required-1):
                points = total_points_requested-(i)*_max_points_per_request
            else:
                points = _max_points_per_request

            try:
                rv = api.get_barset(symbol, time_frame, end = end_date.isoformat(), limit = points)

                # Get the last reported date from the response
                end_date = rv[symbol][0].t
                # print(end_date)


            except Exception as error:
                error_on.append((symbol, error))
                print(f"Error for {symbol}: ")
                print(error)
                pass

            request_time = timer()
            full_rv += rv[symbol]
        
            time.sleep(0.25)  # 0.3 = 200 Querys / 60 Seconds (Alapca API Limit)

        # Get the corresponding stock_id
        write_values = [(f"{stock_id}", p.t, p.o , p.h, p.l, p.c, p.v) for p in full_rv]


        insert_statement = f"""
                                INSERT into {_table_mapping[time_frame]} (stock_id, date_time, open, high, low, close, volume)
                                VALUES %s
                                ON CONFLICT (stock_id, date_time) DO NOTHING
                            """
        db.execute_values(insert_statement, write_values)
        db.commit()
        print(f'Committed {len(write_values)} points into {_table_mapping[time_frame]} for {symbol}')
    
    if len(error_on) > 0:
        print("".join(["Unable to populate the following stocks: \n"]+[f"-\t{ticker} : {error}\n" for (ticker, error) in error_on]))


def get_all_stock_symbols(db : DataBase) -> dict:
    db.execute("SELECT id, symbol from stocks")
    rv = db.cursor.fetchall()
    return {symbol : id for (id, symbol) in rv}

def populate_stocks_table(db : DataBase):
    # Initialize the alpaca API
    api = initialize_alpaca_api()

    # Get the list of tickers
    api._use_raw_data = True
    all_symbols = api.list_assets(status = "active")

    # Build the stock ticker data
    sql_cmd = '''
                INSERT INTO stocks (symbol, name, exchange, shortable, fractionable, class)
                VALUES %s
                ON CONFLICT (symbol) DO NOTHING
            '''
    column_names = db.get_allowable_keys("stocks")[1:]
    vals = []
    for symbol in all_symbols:
        if symbol['tradable'] == True:
            vals.append(tuple([symbol[column] for column in column_names]))

    # Create the DB Object and write to it
    db = DataBase(config.DB_ACCESS[config.DB_LOCATION])
    db.execute_values(sql_cmd, vals)
    db.close_cursor()
    db.commit()
    db.close_connection()


def create_tables(db : DataBase):

    command_list = { "stocks" :[    
                                ''' CREATE TABLE IF NOT EXISTS stocks (
                                    id              SERIAL                  PRIMARY KEY     , 
                                    symbol          TEXT                    NOT NULL UNIQUE , 
                                    name            TEXT                    NOT NULL        ,
                                    exchange        TEXT                    NOT NULL        ,
                                    class           TEXT                    NOT NULL        ,
                                    shortable       BOOLEAN                 NOT NULL        ,
                                    fractionable    BOOLEAN                 NOT NULL        
                                )'''],
                    "trading_days" :
                                ['''
                                    CREATE TABLE IF NOT EXISTS trading_days (
                                    date            DATE            PRIMARY KEY     ,
                                    market_open     BOOLEAN         NOT NULL        ,
                                    close_time      TIME                            ,
                                    open_time       TIME                            ,
                                    session_close   TIME                            ,
                                    session_open    TIME    
                                )'''],

                    "quotes_minutes" :
                                ['''
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
                                )'''],
                    "price_minute"  :
                                ['''CREATE TABLE IF NOT EXISTS price_minute ( 
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
                                '''SELECT create_hypertable('price_minute', 'date_time', if_not_exists => TRUE)'''],

                    "price_hour" : 

                            [    '''CREATE TABLE IF NOT EXISTS price_hour (
                                    stock_id            INTEGER                             NOT NULL,
                                    date_time           TIMESTAMP WITHOUT TIME ZONE         NOT NULL,
                                    open                NUMERIC                             NOT NULL, 
                                    high                NUMERIC                             NOT NULL, 
                                    low                 NUMERIC                             NOT NULL, 
                                    close               NUMERIC                             NOT NULL, 
                                    volume              NUMERIC                             NOT NULL,

                                    PRIMARY KEY (stock_id, date_time),
                                    CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stocks (id)  
                                )     
                                ''',

                                '''CREATE INDEX ON price_hour (stock_id, date_time DESC)''',
                                '''SELECT create_hypertable('price_hour', 'date_time', if_not_exists => TRUE)'''],
                    
                    "price_day" : [

                                '''CREATE TABLE IF NOT EXISTS price_day (
                                    stock_id            INTEGER                             NOT NULL,
                                    date_time           TIMESTAMP WITHOUT TIME ZONE         NOT NULL,
                                    open                NUMERIC                             NOT NULL, 
                                    high                NUMERIC                             NOT NULL, 
                                    low                 NUMERIC                             NOT NULL, 
                                    close               NUMERIC                             NOT NULL, 
                                    volume              NUMERIC                             NOT NULL,

                                    PRIMARY KEY (stock_id, date_time),
                                    CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stocks (id)  
                                )     
                                ''',

                                '''CREATE INDEX ON price_day (stock_id, date_time DESC)''',
                                '''SELECT create_hypertable('price_day', 'date_time', if_not_exists => TRUE)''']
                        }


    for (key, value) in command_list.items():
        [db.cursor.execute(command) for command in value]

    db.cursor.close()
    db.connection.commit()
    db.connection.close()

    print("Tables created")


def populate_trading_days_table(db : DataBase):

    def days_in_range(d1 : date, d2 : date):
        return [d1 + timedelta(days=x) for x in range((d2-d1).days + 1)]

    api = initialize_alpaca_api()

    # Get the list of tickers
    rv = api.get_calendar()
    dates_dict = {day.date.date() : {"open"           : day.open         , 
                                    "session_close" : day.session_close,
                                    "close"         : day.close        ,
                                    "session_open"  : day.session_open}  
                                    for day in rv}
    open_date_list = list(dates_dict.keys())
    all_dates = days_in_range(open_date_list[0], open_date_list[-1])

    vals = []
    for day in all_dates:
        is_trading_day = day in open_date_list
        if is_trading_day:
            day_obj = dates_dict[day]
            val = (day, is_trading_day, day_obj["close"], day_obj["open"], day_obj["session_close"], day_obj["session_open"])
        else:
            val = (day, is_trading_day, None, None, None, None)

        vals.append(val)

    # write to the DB
    sql_cmd = """
                INSERT INTO trading_days
                (date, market_open, close_time, open_time, session_close, session_open)
                VALUES %s
                ON CONFLICT (date) DO NOTHING
            """

    db.execute_values(sql_cmd, vals)

    db.close_cursor()
    db.commit()
    db.close_connection()

def add_latest_data_to_db():
    db = initialize_database()

    stock_dict = get_all_stock_symbols()


if __name__ == "__main__":
    db = initialize_database()

    
    # create_tables(db)
    # stock_names = [*get_all_stock_symbols(db)]
    
    stock_names = ['AAPL','TSLA','GE']
    populate_price_table(db, stock_names, "1Min", 10000)
    # print("end")