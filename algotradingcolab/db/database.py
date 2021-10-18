from psycopg2.extras import execute_batch, execute_values
import psycopg2
import psycopg2.extensions

class DataBase():
    
    # These are static variables that are currently hard-coded, but 
    # eventually we should set these via a request to the DB
    _stocks_table_headers = ["id", "symbol", "name", "exchange", "shortable", "fractionable", "class"]
    _price_minute_table_headers = ["stock_id", "date_time", "open", "high", "low","close", "volume"]

    def __init__(self, access_settings : dict):
        
        if access_settings["CONNECTION"] is not None:
            self._connection = psycopg2.connect(access_settings["CONNECTION"])
            
        else:
            self._connection =    psycopg2.connect(host     = access_settings["DB_HOST"],
                                                   database = access_settings["DB_NAME"],
                                                   user     = access_settings["DB_USER"],
                                                   password = access_settings["DB_PASSWORD"],
                                                   port     = access_settings["DB_PORT"])

        self._curser = self._connection.cursor()
        self._initialized = True

    @staticmethod
    def get_allowable_keys(table_name : str) -> list[str]:
        if table_name == "stocks":
            returnValue = DataBase._stocks_table_headers
        elif table_name == "price_minute":
            returnValue = DataBase._price_minute_table_headers

        return returnValue

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def connection(self) -> psycopg2.extensions.connection:
        return self._connection

    @property
    def cursor(self) -> psycopg2.extensions.cursor:
        return self._curser

    def commit(self) -> None:
        self.connection.commit()
    
    def close_connection(self) -> None:
        self.connection.close()

    def close_cursor(self) ->None:
        self.cursor.close()

    def execute(self, command_str : str):
        return self.cursor.execute(command_str)

    def execute_values(self, sql_cmd : str, vals : list[tuple]):
        return execute_values(self.cursor, sql_cmd, vals)