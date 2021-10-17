from psycopg2.extras import execute_batch, execute_values
import psycopg2


class DataBase():

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

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def connection(self):
        return self._connection

    @property
    def cursor(self):
        return self._curser

    def commit(self) -> None:
        self.connection.commit()
    
    def close_connection(self) -> None:
        self.connection.close()

    def close_cursor(self) -> None:
        self.cursor.close()

    def execute(self, command_str : str):
        return self.cursor.execute(command_str)

    def execute_values(self, sql_cmd : str, vals : tuple):
        return execute_values(self.cursor, sql_cmd, vals)