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
        "python": "$pythonPath -u $fullFileName"
    }
```

Note, the virtual environment and the files for the project do not need to be in the same directory or share the same name. For example, i have the following:
```
virtual env: C:/Users/USER_NAME/.venv/AlgoTrading/
program files: D:/git/AlgoTrading/
```
# Setting up a Docker Image for local Data Base
Take a read through the following: 
* [TimeScaleDB's Guide](https://docs.timescale.com/timescaledb/latest/how-to-guides/install-timescaledb/self-hosted/docker/installation-docker/#docker) on setting up a database through docker
* [Tech Expert's Guide](https://techexpert.tips/timescaledb/timescaledb-docker-installation/) to see how to make data persistent
* [Part Time Larry's YouTube Guide](https://youtu.be/4dwCjaX4QUE?t=604) walks you through installing and testing out the TimescaleDB

# Install dependencies

## Activate your virtual environment
first, ensure your virtual environment is active
```
$ C:/Users/USER_NAME/.venv/ENV_NAME/Scripts/Activate
```
## Install TA-lib
 TA-lib, short for Technical Analysis Library is a C library that has a python wrapper. In order for it to work, the binary files need to be installed. Vist the ["Unofficial Windows Binaries for Python Extension Packages"](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib) and download the relevant .whl package.

 To locate the correct package to install, determine your system's architecture (it is probably 64 bit) and your version of python

 ```bash
 (ENV_NAME) $ python --version   # Prints your current python version (Make sure you are in the virtual env)
 ```
 
 If you are using python version 3.9 on a 64-bit machine, you want TA_Lib‑0.4.21‑cp39‑cp39‑win_amd64.whl. If your version of python is not 3.9, then select the appropriate .whl file to download. 

 Ensuring your virtual environment is active, install the .whl file according to [The Pip documentation](TA_Lib‑0.4.21‑cp39‑cp39‑win_amd64.whl). The following worked for me. Your .whl file name may be different

 ```bash
(ENV_NAME) $ py -m pip install TA_Lib‑0.4.21‑cp39‑cp39‑win_amd64.whl
 ```

## Install from requirements file
```
(ENV_NAME) $ pip install -r requirements.txt
```
 

# Creating the API Keys file

rename the config_template.py file (located in /algotradingcolab/db) to config.py and populate the relevant fields
