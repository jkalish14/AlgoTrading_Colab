from context import algotradingcolab

from algotradingcolab.db.database import DataBase, Stock_Table_Data
from algotradingcolab.db import config


test_dict = {1 : {"symbol"   : "AAPL"         ,
                  "name"     : "Apple"        ,
                  "exchange" : "AMEX"          }}

st = Stock_Table_Data(test_dict)

# Create the local db Object
db =DataBase(config.DB_ACCESS["Local"])


# Check to see if the stocks table contains the data we think it should
resp = db.execute("SELECT * from stocks")
records = db.cursor.fetchmany(10)

st = Stock_Table_Data.init_fromDB(records)
print(st)

assert(st.data[1] == {'symbol': 'AAMC', 'name': 'Altisource Asset Mgmt Corp', 'exchange': 'AMEX'})
