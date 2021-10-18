from database import DataBase
import config


db = DataBase(config.DB_ACCESS[config.DB_LOCATION])

command_list = [    
        ''' CREATE TABLE IF NOT EXISTS stocks (
            id              SERIAL                  PRIMARY KEY     , 
            symbol          TEXT                    NOT NULL UNIQUE , 
            name            TEXT                    NOT NULL        ,
            exchange        TEXT                    NOT NULL        ,
            class           TEXT                    NOT NULL        ,
            shortable       BOOLEAN                 NOT NULL        ,
            fractionable    BOOLEAN                 NOT NULL        
        )''',

        '''
            CREATE TABLE IF NOT EXISTS trading_days (
            date            DATE            PRIMARY KEY     ,
            market_open     BOOLEAN         NOT NULL        ,
            close_time      TIME                            ,
            open_time       TIME                            ,
            session_close   TIME                            ,
            session_open    TIME    
        )''',

        '''
        CREATE TABLE IF NOT EXISTS quotes_minutes (
            stock_id        INTEGER                         NOT NULL,
            date_time       TIMESTAMP WITHOUT TIME ZONE     NOT NULL,
            ask_exchange    TEXT                            NOT NULL,
            ask_price       NUMERIC                         NOT NULL,
            ask_size        NUMERIC                         NOT NULL,
            bid_exchange    TEXT                            NOT NULL,
            bid_price       NUMERIC                         NOT NULL,
            bid_size        NUMERIC                         NOT NULL,
            conditions      TEXT                            NOT NULL,
            tape            TEXT                            NOT NULL,

            PRIMARY KEY (stock_id, date_time),
            CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stocks (id)
        )''',

        '''CREATE TABLE IF NOT EXISTS price_minute ( 
            stock_id            INTEGER                             NOT NULL,
            date_time           TIMESTAMP WITHOUT TIME ZONE         NOT NULL,
            open                NUMERIC                             NOT NULL, 
            high                NUMERIC                             NOT NULL, 
            low                 NUMERIC                             NOT NULL, 
            close               NUMERIC                             NOT NULL, 
            volume              NUMERIC                             NOT NULL,

            PRIMARY KEY (stock_id, date_time),
            CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES stocks (id)
        )''',

        '''CREATE INDEX ON price_minute (stock_id, date_time DESC)''',

        '''SELECT create_hypertable('price_minute', 'date_time', if_not_exists => TRUE)'''
        ]


for command in command_list:
    db.cursor.execute(command)

db.cursor.close()
db.connection.commit()
db.connection.close()

print("Tables created")