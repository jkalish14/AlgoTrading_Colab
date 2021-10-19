from context import algotradingcolab

from algotradingcolab.db.database import DataBase
from algotradingcolab.db import config

a = DataBase(config.DB_ACCESS["Local"])


a.execute("DELETE FROM price_minute")
a.commit()
