import time
""" import requests
#import pyperclip

url = "https://api.binance.com/api/v3/klines"
params = {
    "symbol": "PEPEUSDC",
    "interval": "5m",
    "limit": 5
}

response = requests.get(url, params=params)
data = response.json()

test = []

for i in range(len(data)):
    test.append(data[i][0])

print(test, "\n")

for i in range(len(test)):
    print(time.strftime('%M:%S', time.gmtime(test[i]/1000000))) """

""" tempo = time.time()
print(time.strftime('%M:%S', time.gmtime(tempo)))

time.sleep(2)

tempo2 = time.time()
print(time.strftime('%M:%S', time.gmtime(tempo2)))

print((tempo2-tempo)//2)
print(tempo)
print(tempo2) """

""" old = int(time.strftime('%S', time.gmtime(time.time()))) #ideia que conta os segundos

while True:
    segundo = int(time.strftime('%S', time.gmtime(time.time())))
    print(time.time())
    
    if segundo != old:
        print(segundo)
        old = segundo
        time.sleep(1) """

old = int(time.strftime('%M', time.gmtime(time.time())))

print(old)
""" time.sleep(60-(time.time()%60)) """

while True:
    segundo = int(time.strftime('%M', time.gmtime(time.time())))
    print(time.time())
    
    if segundo != old:
        print(segundo)
        old = segundo
        time.sleep(60)        

#print(f'\n{time.strftime('%M:%S', time.gmtime(tempo/1000))}')

#hh_mm_ss = time.strftime('%H:%M:%S:%MS', time.gmtime(1785160800000/1000))

#print(hh_mm_ss)