
from context import algotradingcolab
from algotradingcolab.db import config
from algotradingcolab.db.database import DataBase

import os

# Test connection to remote DB
DB = DataBase(config.DB_ACCESS["Remote"])
assert(DB.initialized == True)

# Create the local DB Object
DB =DataBase(config.DB_ACCESS["Local"])
assert(DB.initialized == True)

print("Databases are accessable!")

resp = DB.execute("SELECT * from stocks")
records = DB.cursor.fetchmany(10)
assert(records[0] == (1, 'AAMC', 'Altisource Asset Mgmt Corp', 'AMEX'))


print(f"{os.path.splitext(os.path.basename(__file__))[0]} Passed!")


