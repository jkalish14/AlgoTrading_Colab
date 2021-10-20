from context import algotradingcolab

from algotradingcolab.db.database import DataBase
from algotradingcolab.db import config

import talib

import pandas as pd

db = DataBase(config.DB_ACCESS["Local"])

db.drop_tables("DROP TABLE price_minute")
db.commit()
