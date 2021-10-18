from psycopg2.extras import execute_batch, execute_values
import psycopg2
import psycopg2.extensions

class DB_Data():

    def __init__(self):
        self._sql_write_cmd : str  = ""
        self._table         : str  = ""
        self._headers       : list = []
        self._data          : dict = {}

    def to_sql_vals(self):
        pass

    def __repr__(self):
        string = (f"{self.__class__.__name__}"
                  f"(table = {self.table}, headers = {self.headers}, data_length = {len(self.data)})")
        return string

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
    
    @property
    def data(self) -> dict:
        return self._data
    
    @data.setter
    def data(self, vals : dict) -> None:
        self._data = vals

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

    def execute_values(self, sql_cmd : str, vals : tuple):
        return execute_values(self.cursor, sql_cmd, vals)

    def write_data(self,  data : DB_Data):
        return self.execute_values(data.sql_write_cmd, data.to_sql_vals())

    def read_data(self, sql_cmd, fetch_params : tuple[callable, dict], table_data_class : DB_Data):
        
        # Check to make sure the sql command is requesting data from the same table
        # that the provided DB_Data class supports
        if Stock_Table_Data.table not in sql_cmd:
            raise psycopg2.DatabaseError("sql comamnd and provided DB_Data class do not match")

        if table_data_class is Stock_Table_Data:

            resp = self.execute(sql_cmd)

            # Does the function require an argument?
            if fetch_params[1] is None:
                resp = fetch_params[0]()
            else:
                resp = fetch_params[0](**fetch_params[1])

            # If the response is a tuple, turn it to a list
            if type(resp) is tuple:
                resp = [resp]

            obj = Stock_Table_Data.init_fromDB(resp)

        return obj



class Stock_Table_Data(DB_Data):
    
    table : str = "stocks"
    headers : list = DataBase.get_allowable_keys(table)
    
    def __init__(self):
        super().__init__()

    @staticmethod
    def init(stock_info : dict):
        obj = Stock_Table_Data()
        obj.sql_write_cmd = f'''
                                INSERT INTO stocks (symbol, name, exchange, shortable, fractionable, class)
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

        obj.data = stock_info
        
        return obj
    
    @staticmethod
    def init_fromDB(response : list[tuple]):
        headers =  Stock_Table_Data.headers
        data = {}
        for row in response:
            value = {headers[i] : row[i] for i in range(1,len(headers))}
            data[row[0]] = value
        
        return Stock_Table_Data.init(data)
    
    # Overwrites the base classes function
    def to_sql_vals(self) -> str:

        headers = Stock_Table_Data.headers[1:]
        sql_vals = []
        for id in self.data.keys():
            value = {header : self.data[id][header] for header in headers}

            # Format each column as needed
            value["shortable"] = str(value["shortable"]).lower()
            value["fractionable"] = str(value["fractionable"]).lower()

            sql_vals.append(tuple(value.values()))
        return sql_vals

class Price_Table_Data(DB_Data):
    
    table : str = "price_minute"
    headers : list = DataBase.get_allowable_keys(table)
    
    def __init__(self):
        super().__init__()

    @staticmethod
    def init(input_data : dict):
        obj = Price_Table_Data()
        obj.sql_write_cmd = f"""INSERT INTO price_minute
                             (stock_id, date_time, open, high, low, close, volume)
                             VALUES %s 
                             ON CONFLICT (stock_id, date_time) DO NOTHING
                             """

        # Check to make sure the keys match the table column headings
        for key in input_data[list(input_data.keys())[0]].keys():

            if key not in Price_Table_Data.headers:

                valid_headers_str = ""
                for val in Price_Table_Data.headers:
                    valid_headers_str += f'\t - {val} \n'

                error_string = f'''KeyError: \"{key}\" key in provided dictionary does not match a DB column. DB Columns are: \n {valid_headers_str}'''
                print(error_string)
                raise KeyError(f"Invalid Key: {key}")

        obj.data = input_data
        
        return obj
    
    @staticmethod
    def init_fromDB(response : list[tuple]):
        headers =  Price_Table_Data.headers
        data = {}
        for row in response:
            value = {headers[i] : row[i] for i in range(1,len(headers))}
            data[row[0]] = value
        
        return Price_Table_Data.init(data)
    
    # Overwrites the base classes function
    def to_sql_vals(self) -> str:

        headers = Price_Table_Data.headers[2:]
        sql_vals = []
        for (id, time_stamp) in self.data.keys():
            value = tuple([id, time_stamp]+[self.data[(id, time_stamp)][header] for header in headers])
            sql_vals.append(value)
        return sql_vals

