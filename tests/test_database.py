
# from context import algotradingcolab


from algotradingcolab.db import config
from algotradingcolab.db.database import DataBase
from algotradingcolab.helpers.decorators import time_func_execution
from datetime import date, time

import os


@time_func_execution
def get_all_stocks(db : DataBase):
    db.execute("SELECT * from stocks")
    rv = db.cursor.fetchall()
    return rv

def connect_to_database(location : str):
    return DataBase(config.DB_ACCESS[location])

def test_connect_to_local_database():
    local_db = connect_to_database("Local")
    assert(local_db.initialized == True)
    local_db.close_connection()

def test_connect_to_remote_database():
    remote_db = connect_to_database("Remote")
    assert(remote_db.initialized == True)
    remote_db.close_connection()

def test_local_stocks_table():
    db = connect_to_database("Local")
    db.execute("SELECT * from stocks")
    rv = db.cursor.fetchmany(10)
    assert(rv[0] == (1, 'AAMC', 'Altisource Asset Mgmt Corp', 'AMEX', 'us_equity', True, False))

def test_local_dates_table():
    db = connect_to_database("Local")
    db.execute("SELECT * from trading_days")
    rv = db.cursor.fetchmany(10)
    assert(rv[0] == (date(1970, 1, 2), True, time(16, 0), time(9, 30), time(19, 0), time(7, 0)))


# test_local_dates_table()


