from database import DataBase, Stock_Table_Data
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
headers = Stock_Table_Data.headers
dict_keys = Stock_Table_Data.headers[1:]
ticker_data = {} 
i = 0
for obj in all_symbols:
    if obj['tradable'] == True:
        ticker_data[i] = {header : obj[header] for header in dict_keys}
        # ticker_data[i]= {headers[1]: obj['symbol'], headers[2] : obj['name'], headers[3] : obj['exchange']}
        i += 1

stock_tickers = Stock_Table_Data().init(ticker_data)


# Create the DB Object and write to it
db = DataBase(config.DB_ACCESS[config.DB_LOCATION])
db.write_data(stock_tickers)
db.close_cursor()
db.commit()
db.close_connection()

