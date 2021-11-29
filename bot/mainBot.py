from logging import log
import ccxt
import json
from discord import channel
import requests
import fonksiyonlar
import discord
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import time
from discord.ext import tasks, commands
import asyncio

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

    fig.write_image('fig.png')


# discord bot
client = discord.Client()


@client.event
async def on_ready():
    print('bot başladı')


async def background_whale_alert():
    await client.wait_until_ready()
    channel = client.get_channel(id=914825855472119828)

    while not client.is_closed():
        data = func.fetchWhale()
        transactions = data['transactions']
        embedVar = discord.Embed(
            title="Balina Uyarıları ***", description="", color=0x202124)

        for ixa in transactions:
            blockchain = ixa['blockchain']
            symbol = ixa['symbol']
            amount = "${:,.2f}".format(ixa['amount_usd'])
            nereden = ixa['from']['owner_type']
            nereye = ixa['to']['owner_type']
            zaman = ixa['timestamp']
            dt_obj = datetime.fromtimestamp(zaman)
            embedVar.add_field(
                name=f'{blockchain}\n{dt_obj}', value=f'Sembol = {symbol}\nMiktar = {amount}\n( {nereden} -> {nereye} )', inline=True)
        # for end
        await channel.send(embed=embedVar)
        await asyncio.sleep(7200)


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username} : {user_message} ({channel})')

    if message.author == client.user:
        return
    if message.channel.name == 'analiz':
        # YARDIM
        if user_message.lower() == 'yardım':
            embedVar = discord.Embed(
                title="Altay Analiz Botu", description="", color=0xf44336)
            embedVar.add_field(
                name="grafik sembol time", value="Destek-Direnç Gösterir", inline=False)
            embedVar.add_field(
                name="piyasa", value="Güncel piyasa bilgilerini gösterir.", inline=False)
            embedVar.add_field(name="alımdefter sembol",
                               value="Alım emirlerinin yoğunlaştığı bölgeleri gösterir.", inline=False)
            embedVar.add_field(name="satımdefter sembol",
                               value="Satım emirlerinin yoğunlaştığı bölgeleri gösterir.", inline=False)

            await message.channel.send(embed=embedVar)
        # alım ısı haritası
        if user_message.lower().split()[0] == 'alımdefter':
            symbol = user_message.lower().split()[1]
            func.alim_emir(symbol)
            await message.channel.send(file=discord.File('alim.png'))
        # satım ısı haritası
        if user_message.lower().split()[0] == 'satımdefter':
            symbol = user_message.lower().split()[1]
            func.satim_emir(symbol)
            await message.channel.send(file=discord.File('satim.png'))
        # güncel fiyat
        if user_message.lower().split()[0] == 'fiyat':
            symbol = user_message.lower().split()[1]
            price = func.ticker_price(symbol)
            await message.channel.send(f' Güncel Fiyat : {price} USD')

        # destek direnç bölgeleri
        if user_message.lower().split()[0] == 'grafik':
            symbol = user_message.lower().split()[1]
            timezone = user_message.lower().split()[2]
            pair = symbol.upper() + 'USDT'
            if timezone == '4' and timezone == '1':
                await message.channel.send(' ---> 1m - 15m - 30m - 1h - 4h - 1d - 1w  <--- ')
            else:
                get_chart(pair, timezone)
                await message.channel.send(file=discord.File('fig.png'))

        # piyasa durumu
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


TOKEN = 'OTExNTk4MTUwMTk0NzA4NTIw.YZjt7w.WKlFuSWJ4lOTVYB8fUXjLT19hVg'
client.loop.create_task(background_whale_alert())
client.run(TOKEN)
