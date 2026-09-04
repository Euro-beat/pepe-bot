from discord.ext import commands, tasks
import matplotlib.ticker as ticker
from dotenv import load_dotenv
import mplfinance as mpf
from os import getenv
import pandas as pd
import requests
import asyncio
import discord
import signal
import time
import sys
import io

load_dotenv()

DISC_TOKEN = getenv('DISC_TOKEN')

# tenta não explodir o bot ao dar Ctrl + C
def sleep_terminal(signum, frame):
    print('\nBot desligando.\n')
    sleep()
    sys.exit(0)

signal.signal(signal.SIGINT, sleep_terminal)

# Configuração de permissões básicas do bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# função para sincronizar o bot aos segundos
def calcular_espera():
    # Calcula matematicamente o tempo restante para o próximo segundo cheio.
    agora = time.time()
    return 1.0 - (agora % 1)

# {inicialização bot} ---------------------------------------------------------------

print_tempo = False # -> para retornar no chat o retorno da API

@bot.event
async def on_ready():
    print(f'poc-bot #online')

    canal = bot.get_channel(1530050331495628890)
    if canal:
        await canal.send("Bot #online!")
        await canal.send("https://klipy.com/gifs/undertaker-still-alive-1")

    # inicia tarefa que roda a cada X tempo
    if not tarefa_sincronizada.is_running():
            tarefa_sincronizada.start()
            print(f"Iniciado tarefa de verificação contínua.")

# {comandos bot} ---------------------------------------------------------------

@bot.command()
async def sleep(ctx):
    """Desliga o bot"""
    if tarefa_sincronizada.is_running():
        tarefa_sincronizada.stop()
    await ctx.send("Bot #desonline...")
    await ctx.send("https://tenor.com/view/sleep-gif-12944899486400191725")
    await bot.close()
    print('\nBot desligando.\n')

@bot.command()
async def pingar(ctx):
    """Te pinga"""
    await asyncio.sleep(3)
    await ctx.send(f"vai se foder <@{326041751024304139}>")
    print('\nEuro pingado.\n')

# estrutura base para comandos com parâmetros do usuário -> replicável
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

@bot.command()
async def pepe(ctx, *, mensagem: str):
    """Alterna entre ligado e desligado a verificação da API da """
    try:
        global avisar_pepe

        args = mensagem.split(' ')
        if len(args) == 1:
            if "." in args[0]:
                await ctx.send('Condição não indicada como argumento, seguindo com "one".')
                avisar_pepe = (args[0], 'one')
            elif args[0].upper() == 'OFF':
                avisar_pepe = 'off'
            else:
                await ctx.send('Insira o valor PEPE a ser notificado (ou "off"), brow. (exemplo: 0.00000356)')

        elif len(args) == 2:
            if "." in args[0]:
                if args[1] == 'off' or args[1] == 'one' or args[1] == 'always':
                    await ctx.send('Condição registrada.')
                    avisar_pepe = args
                else:
                    await ctx.send('Condição não detectada, seguindo com "one".')
                    avisar_pepe = (args[0], 'one')
                
            else:
                await ctx.send('Insira o valor PEPE a ser notificado, brow. (exemplo: 0.00000356 one)')
            
        else:
            await ctx.send('Número de argumentos demais (2), burro.')

    except Exception as e:
        await ctx.send(f'{e}, burro.')

@pepe.error
async def pepe_error(error):
    global pepe_value
    canal = bot.get_channel(1530050331495628890)

    if isinstance(error, commands.MissingRequiredArgument):
        if canal:
            await canal.send(f'PEPE agora: {pepe_value}')



#{loop get na API Binance}---------------------------------------------------------------------------------------------------


@tasks.loop(seconds=1)
async def tarefa_sincronizada():
    global print_tempo
    global pepe_value
    global avisar_pepe
    # Executa sua lógica exatamente na virada do segundo
    canal = bot.get_channel(1530050331495628890)

    try:
        resposta = requests.get("https://api.binance.com/api/v3/ticker/price", params={"symbol": "PEPEUSDC"})
        
        dados = resposta.json() # symbol e price

        pepe_value = dados["price"]

    except Exception as e:
        await canal.send(f"Ocorreu um erro ao consultar a API: {e}")

    if canal:
        #tempo = time.time()
        if print_tempo:
            # teste de sincronização segundos
            #await canal.send(f"Executando no segundo cheio: {tempo} - {time.strftime('%M:%S', time.gmtime(tempo))}")
            await canal.send(f'PEPE agora: {dados["price"]}')

@tarefa_sincronizada.before_loop
async def antes_da_tarefa():
    """Aguarda o bot se conectar e sincroniza o primeiro disparo."""
    await bot.wait_until_ready()
    
    # Sincroniza a primeira execução perfeitamente com o relógio
    espera = calcular_espera()
    await asyncio.sleep(espera)



# Inicia o bot
try:
    bot.run(DISC_TOKEN)
except KeyboardInterrupt:
    #sleep()
    print("Bot desligando.")

#adicionar confirmação