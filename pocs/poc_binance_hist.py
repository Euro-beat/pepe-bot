import requests
#import pyperclip

url = "https://api.binance.com/api/v3/klines"
params = {
    "symbol": "PEPEUSDC",
    "interval": "5m",
    "limit": 25
}

response = requests.get(url, params=params)
data = response.json()
#pyperclip.copy(data)

prices_low = {}
prices_high = {}

for candle in data:
    #print(f"{data.index(candle)+1} - Lower: {candle[3]}, Higher: {candle[2]}\n")

    try:
        prices_high[candle[2]] += 1
    except KeyError:
        prices_high[candle[2]] = 1

    try:
        prices_low[candle[3]] += 1
    except KeyError:
        prices_low[candle[3]] = 1

print('Lower prices:')
print(prices_low, '\n')

print('Higher prices:')
print(prices_high)