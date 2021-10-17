from db.database import DataBase
from db import config

import alpaca_trade_api as tradeapi

# Initialize the alpaca API
API_ENV = "Paper"
alpaca_api = config.API_SETTINGS["Alpaca"]
api_settings = alpaca_api[API_ENV]
api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')

# Get the list of tickers
api._use_raw_data = True
all_symbols = api.list_assets(status = "active")

# Built the SQL BATCH Request
sql_cmd = '''
INSERT INTO stocks (symbol, name, exchange)
    VALUES %s
'''
sql_vals = []
for obj in all_symbols:
    if obj['tradable'] == True:
        value = (f"\"{obj['symbol'].encode('utf-8').decode('ascii', 'ignore')}\"", f"\"{obj['name'].encode('utf-8').decode('ascii', 'ignore')}\"", f"\"{obj['exchange']}\"")
        sql_vals.append(value)


# Create the DB Object and write to it
db = DataBase(config.DB_ACCESS[config.DB_LOCATION])
db.execute_values(sql_cmd, sql_vals)
db.close_cursor()
db.commit()
db.close_connection()


