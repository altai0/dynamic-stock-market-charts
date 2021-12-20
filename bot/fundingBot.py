import discord
# import requests
# import json
import ccxt
# import time  # botu durduruyor kullanma
from tinydb import TinyDB, Query
import matplotlib.pyplot as plt
from tinydb.operations import delete
import asyncio
from tinydb.queries import where
import fonksiyonlar
import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go

TOKEN = 'OTE0ODQ5MTIyMzgzNzI0NTU1.YaTBow.ouOKIutxB3GAHzoPPMVSLMf_Z08'
edatabase = TinyDB('degisim.json')
exchange = ccxt.binance()
client = discord.Client()
CALCULATE_PUAN = 0
func = fonksiyonlar.funcAnalysis()


def isSupport(df, i):
    support = df['Low'][i] < df['Low'][i-1] and df['Low'][i] < df['Low'][i +
                                                                         1] and df['Low'][i+1] < df['Low'][i+2] and df['Low'][i-1] < df['Low'][i-2]
    return support


def isResistance(df, i):
    resistance = df['High'][i] > df['High'][i-1] and df['High'][i] > df['High'][i +
                                                                                1] and df['High'][i+1] > df['High'][i+2] and df['High'][i-1] > df['High'][i-2]
    return resistance


def get_chart(pair, time):
    binance = ccxt.binance()
    trading_pair = pair
    trading_time = time
    candles = binance.fetch_ohlcv(trading_pair, str(trading_time), limit=120)
    data = pd.DataFrame(candles, columns=['Date',
                                          'Open', 'High', 'Low', 'Close', 'Volume'])
    data = data.iloc[::-1]
    data['Date'] = pd.to_datetime(data['Date'], unit='ms')
    fig = go.Figure(data=[go.Candlestick(x=data['Date'], open=data['Open'],
                                         high=data['High'], low=data['Low'], close=data['Close'], increasing_line_color='gray', decreasing_line_color='#C00000')])
    fig.update_layout(xaxis_rangeslider_visible=False,
                      template='plotly_dark', title=pair + ' - ' + str(trading_time))
    levels = []
    s = np.mean(data['High'] - data['Low'])

    def isFarFromLevel(l):
        return np.sum([abs(l-x) < s for x in levels]) == 0
    levels = []
    for i in range(2, data.shape[0]-2):
        if isSupport(data, i):
            l = data['Low'][i]
            if isFarFromLevel(l):
                levels.append((i, l))
        elif isResistance(data, i):
            l = data['High'][i]
            if isFarFromLevel(l):
                levels.append((i, l))

    for level in levels:
        fig.add_hline(y=level[1], line_dash="dot", row=3, col="all", annotation_text=str(level[1]),
                      annotation_position="bottom right"
                      )

    fig.write_image('destek.png')


@client.event
async def on_ready():
    print('! funding rate analiz botu başladı !')


async def background_task():
    await client.wait_until_ready()
    channel = client.get_channel(id=914892130273624104)

    while not client.is_closed():

        # PUAN UYARI
        ileri = func.ileriSeviyeAnaliz('btc')
        price = func.ticker_price('btc')
        btcNow = datetime.datetime.now()
        btcStringNow = btcNow.strftime("%Y-%m-%d %H:%M")
        kayit = {
            'fonlamaPuan': ileri['fundingRatePuan'],
            'analizPuan': ileri['puan'],
            'fiyat': price,
            'zaman': btcStringNow
        }
        edatabase.insert(kayit)
        fonlamaPuan = ileri['fundingRatePuan']
        cokluAnaliz = ileri['puan']
        await channel.send(f'** Bitcoin Uyarı **\nFonlama Oranı Puanı : `{fonlamaPuan}`\nÇoklu Analiz Puan = `{cokluAnaliz}`\nFiyat = `{price}`\n')

        await asyncio.sleep(14400)


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username} : {user_message} ({channel})')

    if message.author == client.user:
        return
    if message.channel.name == 'analiz':

        if user_message.lower() == 'veri':
            data = edatabase.all()
            embedVar = discord.Embed(
                title="Bitcoin Kayıtlı Veriler", description="", color=0x202124)
            for ix in data:
                fonPuan = ix['fonlamaPuan']
                analizPuan = ix['analizPuan']
                fiyat = ix['fiyat']
                zaman = ix['zaman']
                embedVar.add_field(
                    name=f'FonlamaPuan = `{fonPuan}`\nAnalizPuan = `{analizPuan}`', value=f'{zaman}\nFiyat = `{fiyat}`', inline=True)
            await message.channel.send(embed=embedVar)
        if user_message.lower() == 'piyasa':
            item = func.liqidationCalculate()
            fear = func.get_fear()
            bubbleIndex = func.bitcoinBubbleIndex()

            index = bubbleIndex['bubbleIndex']
            googleTrends = bubbleIndex['googleTrends']
            bitcoinTweets = bubbleIndex['bitcoinTweets']

            fearValue = fear['puan']
            fearName = fear['aciklama']

            long = item['liqLong']
            short = item['liqShort']
            price = func.ticker_price('btc')

            embedVar = discord.Embed(
                title="Bitcoin Piyasa Durumu", description="", color=0xf44336)
            embedVar.add_field(
                name="Güncel Bitcoin Fiyatı", value=f'{price} USD', inline=False)
            embedVar.add_field(
                name="Piyasa Tasfiyesi", value=f'LONG %{long} SHORT %{short} Liquidation', inline=False)
            embedVar.add_field(
                name="Greed & Fear Index", value=f'({fearValue}  {fearName})', inline=False)
            embedVar.add_field(
                name="Bitcoin Bubble Verisi", value=f'( Puan = {index} (100 < Pozitif))\n( Google Trend = {googleTrends})\n( Bitcoin Tweets = {bitcoinTweets})', inline=False)
            await message.channel.send(embed=embedVar)
            return
        # mevcut puanı göster
        if user_message.lower().split()[0] == 'puan':
            symbol = user_message.lower().split()[1]
            price = func.ticker_price(symbol)
            item = func.spesifikFundingCalculate(symbol)
            allData = item['fundingData']
            puan = item['puan']
            # ileri seviye analiz
            ileriSeviyeSonuc = func.ileriSeviyeAnaliz(symbol)
            ileriPuan = ileriSeviyeSonuc['puan']
            pozitifDesc = ileriSeviyeSonuc['pozitifDesc']
            negatifDesc = ileriSeviyeSonuc['negatifDesc']
            # ileriPercentage = ileriSeviyeSonuc['openInterestPercentage']
            embedVar = discord.Embed(
                title="Sonuç ***", description=f'{symbol} - ( {price} USD)', color=0x202124)
            embedVar.add_field(
                name="Fonlama Oranı Puanı", value=f'({puan}) ', inline=False)
            embedVar.add_field(
                name="İleri Seviye Analizi\n(Fonlama Oranı, Korku Endeksi, Açık Pozisyonlar, Fiyat Değişimleri)",
                value=f'Puan = `{ileriPuan}`\nPozitif = `{pozitifDesc}`\nNegatif = `{negatifDesc}`',
                inline=False)
            for dik in allData:
                if dik['rate'] > 0.01:
                    exchange = dik['exchange']
                    rate = dik['rate']
                    embedVar.add_field(
                        name=f'Negatif Etken\n{exchange}', value=f'{rate}', inline=True)
                elif dik['rate'] < 0.01:
                    exchange = dik['exchange']
                    rate = dik['rate']
                    embedVar.add_field(
                        name=f'Pozitif Etken\n{exchange}', value=f'{rate}', inline=True)
                elif dik['rate'] == 0.01:
                    exchange = dik['exchange']
                    rate = dik['rate']
                    embedVar.add_field(
                        name=f'Nötr\n{exchange}', value=f'{rate}', inline=True)
            await message.channel.send(embed=embedVar)
        # fib chart
        if user_message.lower().split()[0] == 'fib':
            symbol = user_message.lower().split()[1]
            timeframe = user_message.lower().split()[2]
            func.fibChart(symbol, timeframe)
            await message.channel.send(file=discord.File('fib.png'))
        # destek direnç
        if user_message.lower().split()[0] == 'grafik':
            symbol = user_message.lower().split()[1]
            timezone = user_message.lower().split()[2]
            pair = symbol.upper() + 'USDT'
            if timezone == '4' and timezone == '1':
                await message.channel.send(' ---> 1m - 15m - 30m - 1h - 4h - 1d - 1w  <--- ')
            else:
                get_chart(pair, timezone)
                await message.channel.send(file=discord.File('destek.png'))
client.loop.create_task(background_task())
client.run(TOKEN)
