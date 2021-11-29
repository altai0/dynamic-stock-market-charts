import discord
import requests
import json
import ccxt
import time
import discord
from tinydb import TinyDB, Query
import asyncio
import fonksiyonlar

TOKEN = 'OTE0ODQ5MTIyMzgzNzI0NTU1.YaTBow.5kC7eK0Ar4UECZ5e12izGqsoH18'
btcDb = TinyDB('btcDb.json')
ethDb = TinyDB('ethDb.json')
exchange = ccxt.binance()
client = discord.Client()

func = fonksiyonlar.funcAnalysis()
LAST_DB_BTC = btcDb.get(doc_id=len(btcDb))
LAST_DB_ETH = ethDb.get(doc_id=len(ethDb))
# print(LAST_DB['puan'])


@client.event
async def on_ready():
    print('! funding rate analiz botu başladı !')


async def background_task():
    await client.wait_until_ready()
    channel = client.get_channel(id=914825855472119828)

    while not client.is_closed():
        print('selam')
        await asyncio.sleep(5)


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username} : {user_message} ({channel})')

    if message.author == client.user:
        return
    if message.channel.name == 'analiz':

        if user_message.lower().split()[0] == 'puan':
            symbol = user_message.lower().split()[1]
            price = func.ticker_price(symbol)
            item = func.spesifikFundingCalculate(symbol)
            allData = item['fundingData']
            puan = item['puan']
            embedVar = discord.Embed(
                title="Algoritma Sonucu ***", description=f'{symbol} - ( {price} USD)', color=0x202124)
            embedVar.add_field(
                name="Hesaplanan Puan", value=f'({puan}) ', inline=False)
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

            await message.channel.send(embed=embedVar)

client.loop.create_task(background_task())
client.run(TOKEN)
