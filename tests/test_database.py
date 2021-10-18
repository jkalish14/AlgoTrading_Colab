
from context import algotradingcolab
from algotradingcolab.db import config
from algotradingcolab.db.database import DataBase
from algotradingcolab.helpers.decorators import time_func_execution

import os

@time_func_execution
def get_all_stocks(database):
    db.execute("SELECT * from stocks")
    rv = db._curser.fetchall()
    return rv

# Test connection to remote db
db = DataBase(config.DB_ACCESS["Remote"])
assert(db.initialized == True)
print("Remote DB is accessable")

# Create the local db Object
db =DataBase(config.DB_ACCESS["Local"])
assert(db.initialized == True)
print("Local DB is accessable")

# Check to see if the stocks table contains the data we think it should
db.execute("SELECT * from stocks")
rv = db._curser.fetchmany(10)
assert(rv[0] == (1, 'AAMC', 'Altisource Asset Mgmt Corp', 'AMEX', 'us_equity', True, False))

get_all_stocks(db)
print(f"{os.path.splitext(os.path.basename(__file__))[0]} Passed!")




