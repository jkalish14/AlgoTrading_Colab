from psycopg2.extras import execute_batch
from database import DataBase
import config

import alpaca_trade_api as tradeapi
import pandas as pd


# Initialize the alpaca API
API_ENV = "Paper"
alpaca_api = config.API_SETTINGS["Alpaca"]
api_settings = alpaca_api[API_ENV]
api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')

# Get the list of tickers from the DB and conver tto a dictionary
db =DataBase(config.DB_ACCESS[config.DB_LOCATION])
db.execute("SELECT id, symbol from stocks")
rv = db.cursor.fetchall()
ticker_dict = {id : ticker for (id, ticker) in rv}

# sql_cmd = '''
#             SELECT * from stocks
#             WHERE id >= 1
#             AND   id < 5
#           '''
sql_cmd = '''
            INSERT into price_minute (stock_id, date_time, open, high, low, close, volume)
            VALUES %s
            ON CONFLICT (stock_id, date_time) DO NOTHING
          '''

end_date = pd.Timestamp.now() - pd.Timedelta(days = 1, minutes=20)
end_date = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
skipped_stocks = []
for (id, ticker) in ticker_dict.items():

    # try:
    rv = api.get_barset(ticker, "1Min", end=end_date, limit= 1000)
    print(f"Adding {ticker} to DataBase")
    vals = [(id, bar.t, bar.o, bar.h, bar.l, bar.c, bar.v) for bar in rv[ticker]]

    db.execute_values(sql_cmd, vals)
    db.commit()
    
    # except Exception as error:
    #     print(error)
    #     skipped_stocks.append((id, ticker))
    #     print(f"Skipped Stock {(id, ticker)}")

    # break

print(skipped_stocks)