

from itsdangerous import exc
from psycopg2.extras import execute_batch
from algotradingcolab.database_management import initialize_alpaca_api
import alpaca_trade_api as tradeapi


def test_init_alapca_api():
    try:
        api = initialize_alpaca_api("paper")
        account = api.get_account()
    except Exception as error:
        raise error

    assert account is not None

