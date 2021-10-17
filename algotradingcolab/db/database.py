from psycopg2.extras import execute_batch, execute_values
import psycopg2
import psycopg2.extensions
from dataclasses import dataclass

# @dataclass
class DB_Data():

    def __init__(self):
        self._sql_write_cmd : str       = ""
        self._table         : str       = ""
        self._headers       : list[str] = []

    def to_sql_vals(self):
        pass

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, vals : list[str]):
        self._headers = vals

    @property
    def sql_write_cmd(self):
        return self._sql_write_cmd

    @sql_write_cmd.setter
    def sql_write_cmd(self, val):
        self._sql_write_cmd = val
    
    @property
    def table(self):
        return self._table
    
    @table.setter
    def table(self, val):
        self._table = val
    

class DataBase():
    
    # These are static variables that are currently hard-coded, but 
    # eventually we should set these via a request to the DB
    _stocks_table_headers = ["id", "symbol", "name", "exchange"]

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

        print("Object Created")

    @staticmethod
    def get_allowable_keys(table_name : str) -> list[str]:
        if table_name == "stocks":
            returnValue = DataBase._stocks_table_headers
        
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

    def execute_values(self, sql_cmd : str, vals : tuple):
        return execute_values(self.cursor, sql_cmd, vals)

    def write_data(self,  data : DB_Data):
        return self.execute_values(data.sql_write_cmd, data.to_sql_vals())

    def read_data(self, sql_cmd, data : DB_Data):
        pass  



class Stock_Table_Data(DB_Data):
    
    table = "stocks"
    headers = DataBase.get_allowable_keys(table)
    
    def __init__(self, stock_info : dict):
        super().__init__()

        # self.headers = DataBase.get_allowable_keys(self.table)
        self.sql_write_cmd = '''
                                INSERT INTO stocks (symbol, name, exchange)
                                VALUES %s
                                ON CONFLICT (symbol) DO NOTHING
                               '''

        # Check to make sure the keys match the table column headings
        for key in stock_info[list(stock_info.keys())[0]].keys():

            if key not in Stock_Table_Data.headers:

                valid_headers_str = ""
                for val in Stock_Table_Data.headers:
                    valid_headers_str += f'\t - {val} \n'

                error_string = f'''KeyError: \"{key}\" key in provided dictionary does not match a DB column. DB Columns are: \n {valid_headers_str}'''
                print(error_string)
                raise KeyError(f"Invalid Key: {key}")

        self._data = stock_info
    
    @property
    def data(self) -> dict:
        return self._data

    @staticmethod
    def init_fromDB(response : list[tuple]):
        headers =  Stock_Table_Data.headers
        data = {}
        for row in response:
            value = {headers[i] : row[i] for i in range(1,len(headers))}
            data[row[0]] = value
        
        return Stock_Table_Data(data)
    
    # Overwrites the base classes function
    def to_sql_vals(self) -> str:

        headers = Stock_Table_Data.headers[1:]
        sql_vals = []
        for id in self.data.keys():
            value = tuple([f"{self.data[id][header].encode('utf-8').decode('ascii', 'ignore')}" for header in headers])
            sql_vals.append(value)
        return sql_vals

