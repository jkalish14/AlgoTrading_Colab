
from algotradingcolab.database import DataBase
from algotradingcolab.database_management import initialize_database

from algotradingcolab import config

# db = DataBase(config.DB_ACCESS["Local"])

# db.drop_tables("DROP TABLE price_minute")
# db.commit()

db = initialize_database()

print("Testing")
