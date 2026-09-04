import requests

try:
        url = "https://api.binance.com/api/v3/ticker/price"
        resposta = requests.get(url, params={"symbol": "PEPEUSDC"})
        
        dados = resposta.json() # symbol e price

        print(dados["price"])

except Exception as e:
    print(f"Ocorreu um erro ao consultar a API: {e}")