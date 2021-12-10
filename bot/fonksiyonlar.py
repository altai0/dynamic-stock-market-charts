import ccxt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np


class funcAnalysis():
    def __init__(self) -> None:
        pass

    def fetchWhale(self):
        req = requests.get(
            'https://api.whale-alert.io/v1/transactions?api_key=H1722a89y8XBb4mRzUpZfPiCFXPpVE3r&min_value=500000&limit=50')
        res = req.json()
        return res

    def bitcoinBubbleIndex(self):
        req = requests.get(
            'https://fapi.coinglass.com/api/index/bitcoinBubbleIndex')
        res = req.json()
        data = res['data'][-1]
        item = {
            'bubbleIndex': data['index'],
            'googleTrends': data['gt'],
            'bitcoinTweets': data['bt'],
            'time': data['time']

        }
        return item

    def avarageFundingRate(self):
        req = requests.get(
            'https://fapi.coinglass.com/api/fundingRate/history/avg/chart?symbol=BTC&type=U&interval=h8')
        res = req.json()
        lastDate = res['data']['dateList'][-1]
        lastPrice = res['data']['priceList'][-1]
        lastRate = res['data']['rateList'][-1]
        item = {
            'time': lastDate,
            'price': lastPrice,
            'avgRate': lastRate
        }
        return item

    def alim_emir(self, symbol):
        binance = ccxt.binance()
        orderbook = binance.fetch_order_book(
            symbol.upper()+'/USDT', limit=1000)
        bids = orderbook['bids']
        fig = go.Figure()
        bids_price = []
        bids_qt = []
        for bid in bids:
            bids_price.append(bid[0])
            bids_qt.append(bid[1])
        d = {'bids_price': bids_price, 'bids_qty': bids_qt}
        df = pd.DataFrame(data=d)

        fig = px.density_heatmap(df, x="bids_price", y="bids_qty",
                                 title='Alım Emirleri Isı Haritası')

        fig.write_image('alim.png')

    def satim_emir(self, symbol):
        binance = ccxt.binance()
        orderbook = binance.fetch_order_book(
            symbol.upper()+'/USDT', limit=1000)
        asks = orderbook['asks']
        fig = go.Figure()
        ask_price = []
        ask_qt = []
        for ask in asks:
            ask_price.append(ask[0])
            ask_qt.append(ask[1])
        d = {'asks_price': ask_price, 'asks_qty': ask_qt}
        df = pd.DataFrame(data=d)

        fig = px.density_heatmap(df, x="asks_price", y="asks_qty",
                                 title='Satım Emirleri Isı Haritası')

        fig.write_image('satim.png')

    def ticker_price(self, symbol):
        try:
            binance = ccxt.binance()
            price_ticker = binance.fetch_ticker(symbol.upper()+'/USDT')
            return price_ticker['last']
        except:
            return 'error'

    def get_fear(self):
        req = requests.get('https://api.alternative.me/fng/')
        result = req.json()
        item = {'puan': result['data'][0]['value'],
                'aciklama': result['data'][0]['value_classification']}
        return item

    def spesifikFundingCalculate(self, symbol):
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
            elif isak['rate'] > 0.025:
                puan -= 16
            elif isak['rate'] < 0.035:
                puan -= 16

        data = {'puan': puan, 'fundingData': fundingRate, 'symbol': sembol}
        return data

    def fundingCalculate(self):
        req = requests.get(
            'https://fapi.coinglass.com/api/fundingRate/v2/home')
        result = req.json()

        fundingRate = []
        for ix in result['data'][0]['uMarginList']:
            if ix['exchangeName'] != 'FTX':
                item = {'exchange': ix['exchangeName'], 'rate': ix['rate']}
                fundingRate.append(item)
        puan = 0
        for isa in fundingRate:
            if isa['rate'] <= 0.01:
                puan += 16
            elif isa['rate'] < 0.035 and isa['rate'] > 0.02:
                puan -= 16
            elif isa['rate'] > 0.035:
                puan -= 16

        data = {'puan': puan, 'fundingData': fundingRate}
        return data

    def liqidationCalculate(self):
        liqReq = requests.get(
            'https://fapi.coinglass.com/api/futures/liquidation/info?symbol=&timeType=1&size=12')
        liqResult = liqReq.json()
        liqidation = [liqResult['data']['ex'][0]]
        item = {'liqShort': liqidation[0]['shortRate'],
                'liqLong': liqidation[0]['longRate']}
        return item

    def ticker_price_24h(self, symbol):
        req = requests.get(
            'https://api.binance.com/api/v3/ticker/24hr?symbol='+symbol.upper()+'USDT')
        res = req.json()
        percentage24h = res['priceChangePercent']
        return percentage24h

    def fetch_open_interest(self):
        req = requests.get(
            'https://fapi.coinglass.com/api/openInterest/v3/chart?symbol=BTC&timeType=0&exchangeName=&type=0')
        res = req.json()
        data = res['data']
        dataMap = data['dataMap']
        # dün ve bugünün total interest kayıt et
        backDay = 0
        nowDay = 0
        for ixa in dataMap:
            if ixa != 'CME' and ixa != 'Kraken' and ixa != 'Bitfinex' and ixa != 'Bitget' and ixa != 'dYdX':
                oldMap = dataMap[ixa][-2]
                nowMap = dataMap[ixa][-1]
                if nowDay != 'None' and oldMap != 'None':
                    nowDay += float(nowMap)
                    backDay += float(oldMap)
        dundenBuguneDegisimOrani = ((nowDay - backDay) / backDay) * 100

        item = {'openPositionYesterday': backDay, 'openPositionToday': nowDay,
                'positionPercentage': dundenBuguneDegisimOrani}
        return item

    def ileriSeviyeAnaliz(self, symbol):

        item = self.spesifikFundingCalculate(symbol)
        percentage = self.ticker_price_24h(symbol)
        fearIndex = self.get_fear()
        openInterest = self.fetch_open_interest()

        puan = 0
        pozitifText = ''
        negatifText = ''
        # pozitif
        if float(fearIndex['puan']) < 50:
            puan += 25
            pozitifText += 'Piyasada korku hakim,'
        if float(item['puan']) > 32:
            pozitifText += 'Fonlama oranları düşük seviyede,'
            puan += 25
        if float(percentage) > 0 and openInterest['positionPercentage'] < 0:
            pozitifText += 'Fiyat yükselirken açık pozisyonlar düşmüş,'
            puan += 25
        if float(percentage) < 0 and openInterest['positionPercentage'] < 0:
            pozitifText += 'Fiyat düşerken açık pozisyonlar düşmüş,'
            puan += 25
        # negatif
        if float(fearIndex['puan']) > 50:
            negatifText += 'Piyasada açgözlülük hakim,'
            puan -= 25
        if float(item['puan']) < 32:
            negatifText += 'Fonlama oranları çok yüksek,'
            puan -= 25
        if float(percentage) > 0 and openInterest['positionPercentage'] > 0:
            negatifText += 'Fiyat artarken açık pozisyonlar yükseliyor,'
            puan -= 25
        if float(percentage) < 0 and openInterest['positionPercentage'] > 0:
            negatifText += 'Fiyat düşerken açık pozisyonlar yükseliyor,'
            puan -= 25
        item = {'puan': puan, 'pozitifDesc': pozitifText,
                'negatifDesc': negatifText, 'fundingRatePuan': item['puan']}
        return item
