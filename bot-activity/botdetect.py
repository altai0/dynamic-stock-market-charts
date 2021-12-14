# requirements
import ccxt
import json
import requests
import asyncio
import numpy as np
import pandas as pd
from tinydb import TinyDB, Query
import websocket
# requirements

# Created By Altai.
# Exchange Bot Detection System
# Version Code : 1.0
# Detection of continuously entered and exited sell orders in bitcoin parity

exchange = ccxt.binance()
database = TinyDB('book.json')

#database.insert(exchange.fetch_order_book('BAL/BTC', limit=1000))

data = database.all()

data_1 = data[-1]  # son kayıt
data_2 = data[-2]
data_3 = data[-3]
data_4 = data[-4]


print(data_4['bids'][0])
