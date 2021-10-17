
from context import algotradingcolab
from algotradingcolab.db import config
from algotradingcolab.db.database import DataBase, Stock_Table_Data

import os

# Test connection to remote db
db = DataBase(config.DB_ACCESS["Remote"])
assert(db.initialized == True)

# Create the local db Object
db =DataBase(config.DB_ACCESS["Local"])
assert(db.initialized == True)

print("Databases are accessable!")

# Check to see if the stocks table contains the data we think it should
st = db.read_data("SELECT * from stocks", (db.cursor.fetchmany, {"size" : 10}), Stock_Table_Data)
assert(st.data[1] == {'symbol': 'AAMC', 'name': 'Altisource Asset Mgmt Corp', 'exchange': 'AMEX'})


print(f"{os.path.splitext(os.path.basename(__file__))[0]} Passed!")




