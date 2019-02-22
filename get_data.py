import ccxt
import os
import sys
import time

exchange = ccxt.binance({'verbose': True})

symbols = exchange.load_markets()

for symbol in symbols:
    cmd = 'python ccxt_market_data.py -e binance -s '+symbol+' -t 1m' 
    print(cmd)
    os.system(cmd)

os.system('move binance ')