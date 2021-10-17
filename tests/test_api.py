from context import algotradingcolab

from algotradingcolab.db import config
from algotradingcolab.db.database import DataBase

import alpaca_trade_api as tradeapi

import os

# Initialize the alpaca API
API_ENV = "Paper"
alpaca_api = config.API_SETTINGS["Alpaca"]
api_settings = alpaca_api[API_ENV]
api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')

account = api.get_account()
assert(account is not None)

print(f"{os.path.splitext(os.path.basename(__file__))[0]} Passed!")
