import matplotlib.ticker as ticker
import mplfinance as mpf
import pandas as pd
import requests
import discord
import io

mensagem = '3m'

"""Gera um gráfico e envia direto no chat"""
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


    # Nota: Em um bot de produção, prefira usar 'aiohttp' em vez de 'requests' 
    # para evitar que o bot trave/congele enquanto espera a resposta da API.
    response = requests.get(url, params=params)
    data = response.json()

    columns = [
        'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 
        'CloseTime', 'QuoteVolume', 'Trades', 'TakerBuyBase', 'TakerBuyQuote', 'Ignore'
    ]
    df = pd.DataFrame(data, columns=columns)

    ##########################
    """ print(df.head())

    df_analise_padrao = df[['High', 'Low']].copy()

    df.to_csv('df.csv', index=False)

    print(df_analise_padrao.head())

    print(df_analise_padrao.value_counts())

    print(f'Máx: {df['High'].mode()[0]} | Min: {df['Low'].mode()[0]}')

    print(df[['High'],['Low']].tail(33).value_counts()) """
    
    #print(f'--últimos 33 valores-- Máx: {df['High'].tail(33).mode()[0]} | Min: {df['Low'].tail(33).mode()[0]}')

    #valores_frequentes = [df['High'].tail(33).mode()[0], df['Low'].tail(33).mode()[0]]
    #print(f'Valores frequentes: {valores_frequentes}')

    #///
    quartil_time = pd.to_datetime(df['Time'].quantile(0.66), unit='ms')
    #print(quartil_time)

    fim_time = pd.to_datetime(df['Time'].iloc[-1], unit='ms')

    df_frequent = df[['High','Low']].copy().tail(33)

    print(df_frequent.value_counts())

    frequent_high = df_frequent['High'].value_counts().index[:4]
    frequent_low = df['Low'].value_counts().index[:4]


    valores_frequentes = []

    # Validações fodas
    for diff in [0.00000003, 0.00000002, 0.00000001]:
        for i in range(3):
            if float(frequent_high[0]) == float(frequent_low[i])+diff:
                valores_frequentes = [frequent_high[0], frequent_low[i]]
        for i in range(3):
            if float(frequent_high[i])-diff == float(frequent_low[0]):
                valores_frequentes = [frequent_high[i], frequent_low[0]]
        for i in range(3):
            if float(frequent_high[1]) == float(frequent_low[i])+diff:
                valores_frequentes = [frequent_high[1], frequent_low[i]]
        for i in range(3):
            if float(frequent_high[i])-diff == float(frequent_low[1]):
                valores_frequentes = [frequent_high[i], frequent_low[1]]

    print(f'Valores frequentes detectados: {valores_frequentes}')

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

    print(f'Max high: {df["High"].max()}')
    print(f'Min low: {df["Low"].min()}')

    # Check para marcação horizontal no gráfico
    graph_amplitude = abs(float(df["High"].max())) - abs(float(df["Low"].min()))
    print(f'Amplitude: {graph_amplitude:.8f}')

    ##########################
    
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

    """ config_vlines = {
        'vlines': quartil_time, # Datas onde as linhas verticais vão passar
        'colors': ['yellow'],           # Cores das linhas
        'linestyle': '--',                      # Estilo ponto e traço
        'linewidths': 1.0    
    } """

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
    mpf.show()