
DB_LOCATION = "Local" # Or "Remote"

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
API_SETTINGS = {"Alpaca" : { "Paper" : {"URL" : "https://paper-api.alpaca.markets",
                                        "KEY" : "YOUR PAPER KEY"},
                             "Live"  : {"URL" : "https://api.alpaca.markets",
                                        "KEY" : "YOUR LIVE KEY"},
                             "Secret_Key" : "YOUR PRIVATE KEY"
                            }
                }

