from algotradingcolab.db import config
from algotradingcolab.helpers.decorators import time_func_execution
import alpaca_trade_api as tradeapi


@time_func_execution
def get_all_stocks(api : tradeapi.REST):
    return api.list_assets()

def init_alapca_api() -> tradeapi.REST:
    # Initialize the alpaca API
    API_ENV = "Paper"
    alpaca_api = config.API_SETTINGS["Alpaca"]
    api_settings = alpaca_api[API_ENV]
    api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')
    return api

def test_init_alapca_api():
    api = init_alapca_api()
    account = api.get_account()
    assert account is not None
