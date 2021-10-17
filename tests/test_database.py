
from context import algotradingcolab
from algotradingcolab.db import config
from algotradingcolab.db.database import DataBase

import os

# Test connection to remote db
db = DataBase(config.DB_ACCESS["Remote"])
assert(db.initialized == True)

# Create the local db Object
db =DataBase(config.DB_ACCESS["Local"])
assert(db.initialized == True)

print("Databases are accessable!")

# Check to see if the stocks table contains the data we think it should
resp = db.execute("SELECT * from stocks")
records = db.cursor.fetchmany(10)
assert(records[0] == (1, 'AAMC', 'Altisource Asset Mgmt Corp', 'AMEX'))


print(f"{os.path.splitext(os.path.basename(__file__))[0]} Passed!")




