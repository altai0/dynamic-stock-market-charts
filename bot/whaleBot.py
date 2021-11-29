from logging import log
from discord import channel
import fonksiyonlar
import discord
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from discord.ext import tasks, commands
import asyncio


func = fonksiyonlar.funcAnalysis()


client = discord.Client()


@client.event
async def on_ready():
    print('whale bot başladı !')


async def background_whale_alert():
    await client.wait_until_ready()
    channel = client.get_channel(id=913371949214875679)

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


TOKEN = 'OTEzMzcxMjU4MDg1ODQ3MDQw.YZ9hRQ.Re58mahpo3729k7CMiUff_zJsyc'
client.loop.create_task(background_whale_alert())
client.run(TOKEN)
