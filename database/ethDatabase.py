import requests
import json
import ccxt
import time
from tinydb import TinyDB, Query
db = TinyDB('ethDb.json')
exchange = ccxt.binance()
print('! eth database kaydı başlatıldı !')

#db.insert({'puan': '50', 'fiyat': '52000', 'zaman': '2021'})
# print(db.all())


def fundingCalculate(symbol):
    req = requests.get(
        'https://fapi.coinglass.com/api/fundingRate/v2/home')
    result = req.json()
    sembol = symbol.upper()

    fundingRate = []
    for ix in result['data']:
        if sembol == ix['symbol']:
            for isa in ix['uMarginList']:
                if len(isa) > 3:
                    item = {
                        'exchange': isa['exchangeName'], 'rate': isa['rate']}
                    fundingRate.append(item)
    puan = 0
    for isak in fundingRate:
        if isak['rate'] <= 0.01:
            puan += 16
        elif isak['rate'] < 0.035 and isak['rate'] > 0.02:
            puan -= 16
        elif isak['rate'] > 0.035:
            puan -= 16
    price = exchange.fetch_ticker(sembol+'/USDT')

    data = {'puan': puan, 'fundingData': fundingRate,
            'symbol': sembol, 'price': price['last']}
    return data


POINT = 0
while True:
    if POINT == 0:
        data = fundingCalculate('eth')
        zaman = time.time()
        item = {'puan': data['puan'], 'fiyat': data['price'], 'zaman': zaman}
        db.insert(item)
        POINT = float(data['puan'])
        print('...ilk kayıt başarılı...' + str(item))
    else:
        data = fundingCalculate('eth')
        if POINT == data['puan']:
            selam = 'değişiklik yok'
        else:
            zaman = time.time()
            item = {'puan': data['puan'],
                    'fiyat': data['price'], 'zaman': zaman}
            db.insert(item)
            POINT = float(data['puan'])
            print('...fiyat değişikliği kayıt edildi...')
    time.sleep(5)
