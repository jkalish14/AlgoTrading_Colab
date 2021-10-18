from database import DataBase
import config

import alpaca_trade_api as tradeapi
# Initialize the alpaca API
API_ENV = "Paper"
alpaca_api = config.API_SETTINGS["Alpaca"]
api_settings = alpaca_api[API_ENV]
api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')

# Get the list of tickers
api._use_raw_data = True
all_symbols = api.list_assets(status = "active")

# Build the stock ticker data
sql_cmd = '''
            INSERT INTO stocks (symbol, name, exchange, shortable, fractionable, class)
            VALUES %s
            ON CONFLICT (symbol) DO NOTHING
          '''
dict_keys = DataBase.get_allowable_keys("stocks")[1:]
vals = []
for obj in all_symbols:
    if obj['tradable'] == True:
        vals.append(tuple([obj[key] for key in dict_keys]))

# Create the DB Object and write to it
db = DataBase(config.DB_ACCESS[config.DB_LOCATION])
db.execute_values(sql_cmd, vals)
db.close_cursor()
db.commit()
db.close_connection()

