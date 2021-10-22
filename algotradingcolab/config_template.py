
DB_LOCATION = "Local"
ALPACA_API_ENV = "paper"

## Database Settings
DB_ACCESS = {"Local" : {
                        "DB_HOST" : "localhost",
                        "DB_NAME" : "timescaledb",
                        "DB_USER" : "postgres",
                        "DB_PASSWORD" : "password",
                        "DB_PORT"   : "5432",
                        "CONNECTION" : None
                        },
            "Remote" : {
                        "DB_HOST" : "localhost",
                        "DB_NAME" : "timescaledb",
                        "DB_USER" : "postgres",
                        "DB_PASSWORD" : "password",
                        "DB_PORT"   : "5432",
                        "CONNECTION" : None
                        # "CONNECTION" : "postgres://BLAHBLAHLBAH"
                        },
            }


## API Settings
API_SETTINGS = {"Alpaca" : { "paper" : {"URL" : "https://paper-api.alpaca.markets",
                                        "KEY" : "YOUR PAPER KEY"},
                             "live"  : {"URL" : "https://api.alpaca.markets",
                                        "KEY" : "YOUR LIVE KEY"},
                             "secret_key" : "YOUR PRIVATE KEY"
                            }
                }

