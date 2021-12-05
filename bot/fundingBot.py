import discord
import requests
import json
import ccxt
import time
import discord
from tinydb import TinyDB, Query
import asyncio

import tinydb
import fonksiyonlar
import datetime

TOKEN = 'OTE0ODQ5MTIyMzgzNzI0NTU1.YaTBow.ouOKIutxB3GAHzoPPMVSLMf_Z08'
edatabase = TinyDB('degisim.json')
exchange = ccxt.binance()
client = discord.Client()
CALCULATE_PUAN = 0
func = fonksiyonlar.funcAnalysis()


@client.event
async def on_ready():
    print('! funding rate analiz botu başladı !')


async def background_task():
    await client.wait_until_ready()
    channel = client.get_channel(id=914892130273624104)

    while not client.is_closed():
        # takip edilen veri kayıdını göster
        takipDatabase = TinyDB('followed.json')
        takipData = takipDatabase.all()
        if len(takipData) != 0:
            for xe in takipData:
                symbol = xe['sembol']
                spItem = func.spesifikFundingCalculate(symbol)
                spPrice = func.ticker_price(symbol)
                spPuan = spItem['puan']
                spNow = datetime.datetime.now()
                spStringNow = spNow.strftime("%Y-%m-%d %H:%M")
                spKayit = {
                    "puan": spPuan,
                    "fiyat": spPrice,
                    "zaman": spStringNow
                }
                spDatabase = TinyDB(f'{symbol}Follow.json')
                spDatabase.insert(spKayit)
        else:
            print('takip edilen sembol yok!')
        # bitcoin kayıt ve göster
        item = func.spesifikFundingCalculate('btc')
        price = func.ticker_price('btc')
        allData = item['fundingData']
        puan = item['puan']

        kayitData = {'puan': puan, 'price': price}
        edatabase.insert(kayitData)
        print('KAYIT YAPILDI')
        # TAKİP ET
        gecmisveri = edatabase.all()

        if gecmisveri[-1]['puan'] == gecmisveri[-2]['puan']:
            embedVar = discord.Embed(
                title="30 Dakikalık Uyarı  ***", description=f'Bitcoin  {price}', color=0x202124)
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
            await channel.send(embed=embedVar)
        else:
            eskiPuan = gecmisveri[-2]['puan']
            embedVar = discord.Embed(
                title="30 Dakikalık Uyarı  ***", description=f'Bitcoin  {price}', color=0x202124)
            embedVar.add_field(
                name="Hesaplanan Puan", value=f'({eskiPuan}) ---> ({puan})', inline=False)
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
            await channel.send(embed=embedVar)
        await asyncio.sleep(1800)


@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    print(f'{username} : {user_message} ({channel})')

    if message.author == client.user:
        return
    if message.channel.name == 'analiz':

        # veritabanındaki verileri göster
        if user_message.lower().split()[0] == 'veri':
            symbol = user_message.lower().split()[1]
            database = TinyDB(f'{symbol}Follow.json')
            data = database.all()
            embedVar = discord.Embed(
                title="Kayıtlı Veriler", description="", color=0x202124)
            for ix in data:
                puan = ix['puan']
                fiyat = ix['fiyat']
                zaman = ix['zaman']
                embedVar.add_field(
                    name=f'Puan : {puan}\n', value=f'{zaman}\nFiyat = {fiyat}', inline=True)
            await message.channel.send(embed=embedVar)
        # veritabanına kayıt
        if user_message.lower().split()[0] == 'takip':
            symbol = user_message.lower().split()[1]
            price = func.ticker_price(symbol)
            if price == 'error':
                await message.channel.send(f'//{symbol}// Hatalı Sembol Girdiniz...')
            else:
                database = TinyDB("followed.json")
                User = Query()
                check = database.search(User.sembol == symbol)
                print(len(check))
                if len(check) == 0:
                    if symbol != 'btc':
                        kayit = {"sembol": symbol}
                        database.insert(kayit)
                        await message.channel.send(f'`{symbol}` için veritabanı takibi açıldı')
                    else:
                        await message.channel.send(f'`{symbol}` takip edemezsiniz')
                else:
                    await message.channel.send(f'`{symbol}` aynı sembolu 2 kez takip edemezsin.')

        # mevcut puanı göster
        if user_message.lower().split()[0] == 'puan':
            symbol = user_message.lower().split()[1]
            price = func.ticker_price(symbol)
            item = func.spesifikFundingCalculate(symbol)
            allData = item['fundingData']
            puan = item['puan']
            embedVar = discord.Embed(
                title="Result ***", description=f'{symbol} - ( {price} USD)', color=0x202124)
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
