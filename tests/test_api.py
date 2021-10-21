
from context import algotradingcolab

from algotradingcolab.database_management import initialize_alpaca_api
import alpaca_trade_api as tradeapi


def test_init_alapca_api():
    api = initialize_alpaca_api()
    account = api.get_account()
    assert account is not None
