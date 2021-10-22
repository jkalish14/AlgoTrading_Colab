
# from context import algotradingcolab

from math import exp

from alpaca_trade_api import rest
from algotradingcolab.database import DataBase
from algotradingcolab.helpers.decorators import time_func_execution
import datetime

from algotradingcolab.database_management import *

TEST_TABLE_NAME = "test_cases_123"
# DATABASE_LOCATIONS = ["Local", "Remote"]

def test_connection_to_database():
    db = initialize_database()
    db.close_connection()
    assert(db.initialized == True)

def test_populate_database():
    try:
        db = initialize_database()
        populate_price_table(db, ["AAMC"], "1Min", 10)
    except Exception as error:
        print(error)
        raise ValueError("Failed to populate database")
    
    assert(True)

def test_stocks_table():
    db = initialize_database()
    db.execute("SELECT * from stocks")
    rv = db.cursor.fetchmany(10)
    assert(rv[0] == (1, 'AAMC', 'Altisource Asset Mgmt Corp', 'AMEX', 'us_equity', True, False))

def test_dates_table():
    db = initialize_database()
    db.execute("SELECT * from trading_days")
    rv = db.cursor.fetchmany(10)
    assert(rv[0] == (datetime.date(1970, 1, 2), True, datetime.time(16, 0), datetime.time(9, 30), datetime.time(19, 0), datetime.time(7, 0)))


def test_create_table():
    did_pass = []
    db = initialize_database()
    
    sql_cmd =   f"""
                    CREATE TABLE IF NOT EXISTS {TEST_TABLE_NAME} (
                        id              SERIAL          PRIMARY KEY ,
                        col1            TEXT            NOT NULL    ,
                        col2            NUMERIC         NOT NULL    ,
                        col3            BOOLEAN         NOT NULL        
                    )
                """
    db.create_tables(sql_cmd)
    
    # Check if the table exists in the DataBase
    sql_cmd =   f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE       table_schema  = 'public'
                    AND         table_name    = '{TEST_TABLE_NAME}'
                )
                """
    db.execute(sql_cmd)
    rv = db.cursor.fetchone()
    did_pass.append(rv == (True,))


    # Check if the table exists in the DataBase object
    did_pass.append(db.check_if_table_exists(TEST_TABLE_NAME) == True)

    for header in ["id", "col1", "col2", "col3"]:
        did_pass.append(db.check_if_header_exists((TEST_TABLE_NAME,header)) == True)


    assert(all(did_pass) == True)


def test_execute_values():


    db = initialize_database()

    sql_cmd =   f"""INSERT INTO {TEST_TABLE_NAME} (col1, col2, col3)
                    VALUES %s
                    ON CONFLICT (id) DO NOTHING
                """
    vals = [("TESTING1", 1, True),
            ("TESTING2", 2, False),
            ("TESTING3", 3, False)]
    
    db.execute_values(sql_cmd, vals)
    db.commit()

    db.execute(f"SELECT * from {TEST_TABLE_NAME}")
    rv = db.cursor.fetchone()
    assert(rv == (1, 'TESTING1', 1, True))

def test_drop_tables():
    
        did_pass = {}

        db = initialize_database()
        
        db.drop_tables(TEST_TABLE_NAME)

        # Make sure it was removed from the table
        sql_cmd =   f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE       table_schema  = 'public'
                            AND         table_name    = '{TEST_TABLE_NAME}'
                        )
                    """
        db.execute(sql_cmd)
        rv = db.cursor.fetchone()
        did_pass["Check table gone SQL"] = (rv == (False,))

        # Make sure the DataBase object was updated
        try:
            db.check_if_table_exists(TEST_TABLE_NAME)
        except KeyError as error:
            print(error)
            did_pass["Check Table gone DataBase Class"] = True
        
        assert all(did_pass.values()) == True,  "".join(["Failed Test, see below: \n"] + [f"\t-{key} : {value}\n" for (key,value) in did_pass.items()])


def test_tables_exists():
    
    expected_tables = ["stocks", "trading_days", "quotes_minutes", "price_minute"]
    db = initialize_database()

    db_table_names = [*db.tables]
    
    did_pass = []
    results = []

    for table in expected_tables:

        in_table = True if table in db_table_names else False
        did_pass.append(in_table)
        results.append((in_table, table))
    
    assert all(did_pass), "".join(["Failed test, see result pairs \n"] + [f"\t - {pair}\n" for pair in results])
    