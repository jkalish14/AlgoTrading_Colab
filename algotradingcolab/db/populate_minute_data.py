from database import DataBase, Stock_Table_Data, Price_Table_Data
import config

import alpaca_trade_api as tradeapi

# Initialize the alpaca API
API_ENV = "Paper"
alpaca_api = config.API_SETTINGS["Alpaca"]
api_settings = alpaca_api[API_ENV]
api = tradeapi.REST(api_settings["KEY"], alpaca_api["Secret_Key"], api_settings["URL"], api_version='v2')

# 
db =DataBase(config.DB_ACCESS["Local"])
# sql_cmd = '''
#             SELECT * from stocks
#             WHERE id >= 1
#             AND   id < 5
#           '''
sql_cmd = '''
            SELECT * from stocks
          '''
std = db.read_data(sql_cmd, (db.cursor.fetchall, None), Stock_Table_Data)

for stock_id, vals in std.data.items():
    print(f'Processing {std.data[stock_id]["symbol"]}')
    response = api.get_bars(vals['symbol'], "1Min", "2021-10-15", "2021-10-16") 
    data = {}
    for point in response:
        data[(stock_id, str(point.t))] = {"open" : point.o, "high" : point.h,  "low" : point.l, "close" : point.c, "volume" : point.v}

    try:
        ptd = Price_Table_Data.init(data)
        db.write_data(ptd)
    except:
        print("Skipped")

db.close_cursor()
db.commit()
db.close_connection()
