from database import DataBase
import config

import alpaca_trade_api as tradeapi
from datetime import date, timedelta

def days_in_range(d1 : date, d2 : date):
    return [d1 + timedelta(days=x) for x in range((d2-d1).days + 1)]

# Initialize the alpaca API
API_ENV = "Paper"
alpaca_api = config.API_SETTINGS["Alpaca"]
api_settings = alpaca_api[API_ENV]
api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')

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

# Initialize the DB and write to it
db =DataBase(config.DB_ACCESS[config.DB_LOCATION])
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