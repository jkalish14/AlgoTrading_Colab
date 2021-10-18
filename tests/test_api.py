from context import algotradingcolab

from algotradingcolab.db import config
from algotradingcolab.helpers.decorators import time_func_execution
import alpaca_trade_api as tradeapi

import os

@time_func_execution
def get_all_stocks(api : tradeapi.REST):
    api.list_assets()


# Initialize the alpaca API
API_ENV = "Paper"
alpaca_api = config.API_SETTINGS["Alpaca"]
api_settings = alpaca_api[API_ENV]
api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')

account = api.get_account()
assert(account is not None)

get_all_stocks(api)
print(f"{os.path.splitext(os.path.basename(__file__))[0]} Passed!")
