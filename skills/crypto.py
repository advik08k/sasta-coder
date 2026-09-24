import requests, sys
symbol = sys.argv[1].upper() if len(sys.argv) > 1 else "BTCUSDT"
if not symbol.endswith("USDT"): symbol += "USDT"
try:
    r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
    print(f"Price of {symbol}: ")
except:
    print("Could not fetch price. Make sure symbol is correct (e.g. BTC, ETH)")
