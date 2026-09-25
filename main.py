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

avisar_pepe = (None, 'off')

@bot.event
async def on_ready():
    print('\npepe-bot #online\n')

    canal = bot.get_channel(1530050331495628890)
    if canal:
        await canal.send(f"Bot #online! <@{326041751024304139}>")
        await canal.send("https://klipy.com/gifs/undertaker-still-alive-1")

    # inicia tarefa que roda a cada X tempo
    if not tarefa_sincronizada.is_running():
            tarefa_sincronizada.start()
            print(f"Iniciado tarefa de verificação contínua.\n")

# {comandos bot} ---------------------------------------------------------------


@bot.command()
async def sleep(ctx):
    """Desliga o bot"""
    if tarefa_sincronizada.is_running():
        tarefa_sincronizada.stop()
    await ctx.send(f"Bot #desonline... <@{326041751024304139}>")
    await ctx.send("https://tenor.com/view/sleep-gif-12944899486400191725")
    await bot.close()
    print('\nBot desligado.\n')

# {comando} ---------------------------------------------------------------

@bot.command()
async def pingar(ctx, *, mensagem: float):
    """Te pinga"""
    try:
        await asyncio.sleep(mensagem)
        await ctx.send(f"vai se foder <@{326041751024304139}>")
        print('\nEuro pingado.\n')
    except Exception as e:
            await ctx.send(f'{e}, burro.')

@pingar.error
async def teste_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        try:
            await ctx.send(f"vai se foder <@{326041751024304139}>")
            print('\nEuro pingado.\n')
        except Exception as e:
            await ctx.send(f'{e}, burro.')

# {comando} ---------------------------------------------------------------

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

# {comando} ---------------------------------------------------------------

@bot.command()
async def grafico(ctx, *, mensagem: str):
    """Retorna o gráfico de preço histórico no chat"""
    try:
        if ' ' in mensagem:
            print('Número de argumentos demais (1), burro.')
        elif 'm' not in mensagem and 'h' not in mensagem:
            print('Precisa definir o tipo de intervalo (m/h), brow...')
        else:
            url = "https://api.binance.com/api/v3/klines"

            params = {
                "symbol": "PEPEUSDC",
                "interval": mensagem,
                "limit": 100
            }

            response = requests.get(url, params=params)
            data = response.json()

            columns = [
                'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                'CloseTime', 'QuoteVolume', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore'
            ]
            df = pd.DataFrame(data, columns=columns)

            # Análise do gráfico
            quartil_time = pd.to_datetime(df['Time'].quantile(0.66), unit='ms')

            fim_time = pd.to_datetime(df['Time'].iloc[-1], unit='ms')

            frequent_high = df['High'].value_counts().index[:4]
            frequent_low = df['Low'].value_counts().index[:4]

            valores_frequentes = []

            # Validações fodas
            for diff in [0.00000003, 0.00000002, 0.00000001]:
                for i in range(3):
                    if float(frequent_high[0]) == float(frequent_low[i]) + diff:
                        valores_frequentes = [frequent_high[0], frequent_low[i]]
                for i in range(3):
                    if float(frequent_high[i]) - diff == float(frequent_low[0]):
                        valores_frequentes = [frequent_high[i], frequent_low[0]]
                for i in range(3):
                    if float(frequent_high[1]) == float(frequent_low[i]) + diff:
                        valores_frequentes = [frequent_high[1], frequent_low[i]]
                for i in range(3):
                    if float(frequent_high[i]) - diff == float(frequent_low[1]):
                        valores_frequentes = [frequent_high[i], frequent_low[1]]

            try:
                valores_frequentes_format = [
                    [(quartil_time, float(valores_frequentes[0])), (fim_time, float(valores_frequentes[0]))],
                    [(quartil_time, float(valores_frequentes[1])), (fim_time, float(valores_frequentes[1]))]
                ]

            except IndexError:
                print('Nenhum valor frequente detectado.')
                valores_frequentes_format = []

            except Exception as e:
                print(f'Erro excepcional: {e}')

            # Check para gridlines no gráfico
            graph_amplitude = abs(float(df["High"].max())) - abs(float(df["Low"].min()))

            # Fim
            
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

            config_hlines = {
                        'alines': valores_frequentes_format, # Datas onde as linhas verticais vão passar
                        'colors': ['blue', 'blue'],           # Cores das linhas
                        'linestyle': '-',                      # Estilo ponto e traço
                        'linewidths': 0.5    
                    }
            
            # Geramos a figura através do mplfinance
            fig, axlist = mpf.plot(
                df, 
                type='candle', 
                style=mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=cores_mercado),
                ylabel='',
                volume=False,
                returnfig=True,
                alines=config_hlines,
                show_nontrading=True,
                #vlines = config_vlines
                #figratio=(20, 15)
            )

            # Verifica se o gráfico tem muitos valores distintos para traçar o grid
            if graph_amplitude <= 0.00000030:
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

# {comando} ---------------------------------------------------------------

@bot.command()
async def pepe(ctx, *, mensagem: str):
    """Consulta valor atual ou configura alerta de preço"""
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
async def pepe_error(ctx, error):
    global pepe_value
    #canal = bot.get_channel(1530050331495628890)

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'PEPE agora: {pepe_value}')


# {loop GET na API Binance}---------------------------------------------------------------------------------------------------


@tasks.loop(seconds=1)
async def tarefa_sincronizada():
    global pepe_value
    global avisar_pepe

    canal = bot.get_channel(1552912057320345642)

    try:
        resposta = requests.get("https://api.binance.com/api/v3/ticker/price", params={"symbol": "PEPEUSDC"})
        
        dados = resposta.json() # symbol e price

        pepe_value = dados["price"]

    except Exception as e:
        await canal.send(f"Ocorreu um erro ao consultar a API: {e}")

    if canal:
        match avisar_pepe[1]:
            case 'always':
                if avisar_pepe[0] == pepe_value:
                    await canal.send(f'PEPE bateu o valor indicado: {dados["price"]} <@{326041751024304139}>')
            case 'one':
                if avisar_pepe[0] == pepe_value:
                    await canal.send(f'PEPE bateu o valor indicado: {dados["price"]} <@{326041751024304139}>')
                    avisar_pepe[1] = 'off'


@tarefa_sincronizada.before_loop
async def antes_da_tarefa():
    """Aguarda o bot se conectar e sincroniza o primeiro disparo."""
    await bot.wait_until_ready()
    
    # Sincroniza a primeira execução perfeitamente com o relógio
    espera = calcular_espera()
    await asyncio.sleep(espera)


# {CONSEGUE desligar o bot com segurança com Ctrl + C terminal}---------------------------------------------------------------------------------------------------

async def sleep_terminal():
    """Desliga o bot com Ctrl + C"""
    if tarefa_sincronizada.is_running():
        tarefa_sincronizada.stop()

    canal = bot.get_channel(1530050331495628890)

    if canal:
        await canal.send(f"Bot #desonline... <@{326041751024304139}>")
        await canal.send("https://tenor.com/view/sleep-gif-12944899486400191725")
        await bot.close()
        print('\nBot desligado.\n')

def explode_bot(signum, frame):
    try:
        if bot.loop and bot.loop.is_running():
            print("\nExplodindo o bot...\n")
            
            # Cria uma tarefa em segundo plano dentro do loop do bot
            # Isso impede o erro de 'never awaited'
            asyncio.run_coroutine_threadsafe(sleep_terminal(), bot.loop)
            return
            
    except Exception as e:
        print(f"Erro ao explodir o bot: {e}")

    sys.exit(0)

signal.signal(signal.SIGINT, explode_bot)

# {inicia o bot}---------------------------------------------------------------------------------------------------

try:
    bot.run(DISC_TOKEN)
except Exception as e:
    print(f"Erro ao tentar iniciar o bot: {e}")

#TODO: adicionar resumo quando chamar !grafico (amplitude, valores mais repetidos, etc)
#TODO: adicionar API de buy/sell e super confirmação