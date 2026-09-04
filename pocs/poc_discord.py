import matplotlib.ticker as ticker
from discord.ext import commands
#import matplotlib.pyplot as plt
from dotenv import load_dotenv
import mplfinance as mpf
from os import getenv
import pandas as pd
#import threading
import requests
import asyncio
import discord
import signal
import time
import sys
import io

load_dotenv()

# Substitua pelo Token gerado no painel de desenvolvedor do Discord
DISC_TOKEN = getenv('DISC_TOKEN')

def sleep_term(signum, frame):
    print('\nBot desligando.\n')
    sys.exit(0)

signal.signal(signal.SIGINT, sleep_term)

# Configuração de permissões básicas do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Funções que executam as tarefas em segundo plano (Threads)
def minha_tarefa_pesada():
    print("Script principal iniciado à distância via Discord!")
    time.sleep(1)
    print("Script principal concluído!")

def dor():
    for i in range(5):
        print('Executando ação secundária...\n')

# Criando a interface de botões que aparecerá no Discord
class ControleRemotoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="🚀 Autorizar Script", style=discord.ButtonStyle.blurple)
    async def confirmar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Envia uma mensagem comum no canal e avisa o Discord que o botão foi clicado
        await interaction.channel.send("Disparando script principal...")
        await interaction.response.defer()
        
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        await asyncio.to_thread(minha_tarefa_pesada)
        await interaction.message.delete()

    @discord.ui.button(label="💀 Rodar Função Secundária", style=discord.ButtonStyle.danger)
    async def declinar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Envia uma mensagem comum no canal e avisa o Discord que o botão foi clicado
        await interaction.channel.send("Disparando função secundária...")
        await interaction.response.defer()
        
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        await asyncio.to_thread(dor)
        await interaction.message.delete()

@bot.event
async def on_ready():
    print(f'poc-bot #online')

    canal = bot.get_channel(1530050331495628890)
    if canal:
        await canal.send("Bot #online!")
        await canal.send("https://klipy.com/gifs/undertaker-still-alive-1")        

# Comando para invocar o painel de controle no chat
@bot.command()
async def painel(ctx):
    """Exemplo de botões criado para mostrar como funciona"""
    view = ControleRemotoView()
    await ctx.send("🎛️ **Painel de Controle Remoto**\nEscolha uma ação abaixo:", view=view)

@bot.command()
async def sleep(ctx):
    """Desliga o bot"""
    await ctx.send("Bot #desonline...")
    await ctx.send("https://tenor.com/view/sleep-gif-12944899486400191725")
    await bot.close()
    print('\nBot desligando.\n')

@bot.command()
async def pingar(ctx):
    """Retorna um ping"""
    sleep(3)
    await ctx.send(f"vai se foder <@{326041751024304139}>")
    print('\nEuro pingado.\n')

@bot.command()
async def teste(ctx, *, mensagem: str):
    """Testa o input com 2 parâmetros obrigatórios"""
    try:
        args = mensagem.split(' ')
        if len(args) < 2:
            await ctx.send('Número de argumentos insuficientes (2), burro.')
        elif len(args) > 2:
            await ctx.send('Número de argumentos demais (2), burro.')
        else:
            await ctx.send(f'Argumento 1: {args[0]}\nArgumento 2: {args[1]}')
    except Exception as e:
        await ctx.send(f'{e}, burro.')

@teste.error
async def teste_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Número de argumentos insuficientes (2), burro.')

@bot.command()
async def grafico(ctx, *, mensagem: str):
    """Gera um gráfico e envia direto no chat"""
    try:
        if ' ' in mensagem:
            await ctx.send('Número de argumentos demais (1), burro.')
        elif 'm' not in mensagem and 'h' not in mensagem:
            await ctx.send('Precisa definir o tipo de intervalo (m/h), brow...')
        else:
            url = "https://api.binance.com/api/v3/klines"

            params = {
                "symbol": "PEPEUSDC",
                "interval": mensagem,
                "limit": 100
            }

            # Nota: Em um bot de produção, prefira usar 'aiohttp' em vez de 'requests' 
            # para evitar que o bot trave/congele enquanto espera a resposta da API.
            response = requests.get(url, params=params)
            data = response.json()
            
            columns = [
                'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                'CloseTime', 'QuoteVolume', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore'
            ]
            df = pd.DataFrame(data, columns=columns)
            
            df['Time'] = pd.to_datetime(df['Time'], unit='ms')
            df.set_index('Time', inplace=True)
            
            numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

            cores_mercado = mpf.make_marketcolors(
                up='#2ebd85', 
                down='#f6465d', 
                edge='inherit', 
                wick='inherit'
            )
            
            # Geramos a figura através do mplfinance
            fig, axlist = mpf.plot(
                df, 
                type='candle', 
                style=mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=cores_mercado),
                ylabel='',
                volume=False,
                returnfig=True,
                #figratio=(20, 15)
            )

            axlist[0].yaxis.set_major_locator(ticker.MultipleLocator(0.00000001))
            axlist[0].yaxis.set_major_formatter(ticker.FormatStrFormatter('%.8f'))
            
            # Cria o buffer de memória
            buffer = io.BytesIO()
            
            fig.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            
            # Transforma o buffer no arquivo anexável do Discord
            imagem = discord.File(buffer, filename=f"PEPEUSDC_{mensagem}.png")
            
            # Envia a mensagem de texto com o anexo embaixo
            await ctx.send(f"Aqui está o gráfico que você pediu ({mensagem}):", file=imagem)

    except Exception as e:
        await ctx.send(f'{e}, burro.')

@grafico.error
async def teste_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Número de argumentos insuficiente (1), burro.')

# Inicia o bot
try:
    bot.run(DISC_TOKEN)
except KeyboardInterrupt:
    #sleep()
    print("Bot desligando.")

#adicionar confirmação