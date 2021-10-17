# Getting Started


# Setting up Virtual Environment with Python venv

Read through the [Python Venv Docs](https://docs.python.org/3/tutorial/venv.html) and setup your virtual environment. I setup mine by creating a .venv directory in my user folder
```
$ cd C:/Users/USER_NAME/.venv
$ python -m venv ENV_NAME
$ C:/Users/USER_NAME/.venv/ENV_NAME/Scripts/Activate
```
Then point VSCode to the python instance located at C:/Users/USER_NAME/.venv/ENV_NAME/Scripts/python.exe 

if you are using code-runner add the following into your workspace .code-workspace "settings" 
```
    "code-runner.executorMap": {
        "python": "C:/Users/USER_NAME/.venv/ENV_NAME/Scripts/python.exe -u"
    }
```

Note, the virtual environment and the files for the project do not need to be in the same directory or share the same name. For example, i have the following:
```
virtual env: C:/Users/USER_NAME/.venv/AlgoTrading/
program files: D:/git/AlgoTrading/
```

# Install dependencies
```
$ C:/Users/USER_NAME/.venv/ENV_NAME/Scripts/Activate
$ pip install -r requirements.txt
```

# Creating the API Keys file

Create a file called "apikeys.json" in the root directory and fill it with the following information. YOUR_PAPER_PUBLIC_KEY, YOUR_LIVE_PUBLIC_KEY, and YOUR_PRIVATE_KEY can be found from your alpaca dashboard
```
{
    "Services": {
        "Supported" : ["Alpaca"],
        "Alpaca" : {
            "Paper_Trading" : {
                "End_Point" : "https://paper-api.alpaca.markets",
                "API_Public_Key"   : "YOUR_PAPER_PUBLIC_KEY"
            },
            "Live_Trading" : {
                "End_Point" : "https://api.alpaca.markets",
                "API_Public_Key"   : "YOUR_LIVE_PUBLIC_KEY"
            },
            "API_Secret_Key"   : "YOUR_PRIVATE_KEY"

        }
    }
}
```