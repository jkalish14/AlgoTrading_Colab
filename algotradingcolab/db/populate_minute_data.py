from database import DataBase
import config

import alpaca_trade_api as tradeapi

# Initialize the alpaca API
API_ENV = "Paper"
alpaca_api = config.API_SETTINGS["Alpaca"]
api_settings = alpaca_api[API_ENV]
api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')

# 
db =DataBase(config.DB_ACCESS["Local"])
# sql_cmd = '''
#             SELECT * from stocks
#             WHERE id >= 1
#             AND   id < 5
#           '''
sql_cmd = '''
            SELECT * from stocks
          '''
