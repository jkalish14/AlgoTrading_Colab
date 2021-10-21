from context import algotradingcolab

from algotradingcolab.db.database import DataBase
from algotradingcolab import config

db = DataBase(config.DB_ACCESS["Local"])

db.drop_tables("DROP TABLE price_minute")
db.commit()


