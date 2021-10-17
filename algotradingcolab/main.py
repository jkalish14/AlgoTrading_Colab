

from db.database import DataBase
from db import config

db = DataBase(config.DB_ACCESS[config.DB_LOCATION])