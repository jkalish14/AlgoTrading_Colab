from psycopg2.extras import execute_batch, execute_values
import psycopg2
import psycopg2.extensions


class DataBase():

    def __init__(self, access_settings : dict):
        
        try: 
            if access_settings["CONNECTION"] is not None:
                self.connection = psycopg2.connect(access_settings["CONNECTION"])
                
            else:

                self.connection =    psycopg2.connect(host     = access_settings["DB_HOST"],
                                                    database = access_settings["DB_NAME"],
                                                    user     = access_settings["DB_USER"],
                                                    password = access_settings["DB_PASSWORD"],
                                                    port     = access_settings["DB_PORT"])

            self.cursor = self._connection.cursor()
            self.initialized = True
            self.populate_tables_dict()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            self.initialized = False

    def __del__(self):
        self.close_cursor()
        self.close_connection()

    def check_if_table_exists(self, table_name : str) -> bool:
        if table_name not in self.tables:
            error_str = [f"The requested table, {table_name}, does not exist in the Database \nThe Database contains the following tables: \n"]
            error_str += [f"\t - {key} \n" for key in self.tables]
            print("".join(error_str))
            raise KeyError
        
        return True

    def check_if_header_exists(self, table_header : tuple) -> bool:
        (table_name, header_name) = table_header
        self.check_if_table_exists(table_name)
        if header_name not in self.tables[table_name]:
            error_str = [f"The requested header, {header_name}, does nto exist in table {table_name}"
                         f"The table contains the following headers: \n"]
            error_str += [f"\t - {header} \n" for header in self.tables[table_name]]
            print("".join(error_str))
            raise KeyError
        
        return True

    def create_tables(self, sql_cmd : str):
        self.execute(sql_cmd)
        self.commit()
        self.populate_tables_dict()

    def drop_tables(self, table_name : str):
        self.execute(f"DROP TABLE {table_name}")
        self.commit()
        self.populate_tables_dict()

    def get_allowable_keys(self, table_name : str) -> list[str]:
        self.check_if_table_exists(table_name)
        return self.tables[table_name]

    def populate_tables_dict(self):
        # To get list of tables
        sql_cmd =   """
                        SELECT * 
                        FROM pg_catalog.pg_tables
                        WHERE schemaname = 'public'
                    """

        self.execute(sql_cmd)
        rv = self.cursor.fetchall()
        
        self.tables = { table_property[1] : None for table_property in rv}

        for table in list(self.tables.keys()):

            # To get columns of each table
            sql_cmd =   f"""
                            SELECT * 
                            FROM information_schema.columns
                            WHERE table_name = '{table}'
                        """

            self.execute(sql_cmd)
            rv = self.cursor.fetchall()
            
            self.tables[table] = [header[3] for header in rv]
        

    @property
    def tables(self) -> dict:
        return self._tables

    @tables.setter
    def tables(self, val : dict):
        self._tables = val

    @property
    def initialized(self) -> bool:
        return self._initialized
    
    @initialized.setter
    def initialized(self, val):
        self._initialized = val

    @property
    def connection(self) -> psycopg2.extensions.connection:
        return self._connection

    @connection.setter
    def connection(self, con : psycopg2.extensions.connection):
        if type(con) is not psycopg2.extensions.connection:
            raise ValueError
    
        self._connection = con

    @property
    def cursor(self) -> psycopg2.extensions.cursor:
        return self._curser

    @cursor.setter
    def cursor(self, val : psycopg2.extensions.cursor):
        if type(val) is not psycopg2.extensions.cursor:
            raise ValueError

        self._curser = val

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
