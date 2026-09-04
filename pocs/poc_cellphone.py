from flask import Flask, render_template_string, redirect, url_for
import threading
import time

app = Flask(__name__)

# Variável para controlar o estado da execução
status_script = "Aguardando confirmação..."

def minha_tarefa_pesada():
    global status_script
    status_script = "Executando o script principal..."
    
    # --- INSIRA SEU SCRIPT PYTHON AQUI ---
    print("Script iniciado à distância!")
    time.sleep(5) # Simula o script rodando
    # -------------------------------------
    
    status_script = "Executado com sucesso! Aguardando próxima."

def dor():
    for i in range(5):
        print('bucetões 🤤\n')

@app.route('/')
def home():
    # Página simples com um botão que o celular vai renderizar
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Controle Remoto Python</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial; text-align: center; margin-top: 50px; background: #f0f2f5; }}
            .btn {{ padding: 20px 40px; font-size: 20px; color: white; background: #007bff; border: none; border-radius: 8px; cursor: pointer; }}
            .btndor {{ padding: 20px 40px; font-size: 20px; color: white; background: #ff0000; border: none; border-radius: 8px; cursor: pointer; }}
            .status {{ margin-top: 30px; font-weight: bold; color: #333; }}
        </style>
    </head>
    <body>
        <h2>Controle do Script</h2>
        <p class="status">Status Atual: {status_script}</p>
        <form action="/confirmar" method="post">
            <button type="submit" class="btn">🚀 Autorizar e Rodar Script</button>
        </form>
        <form action="/declinar" method="post">
                    <button type="submit" class="btndor">💀 Sla se matar porra</button>
            </form>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/confirmar', methods=['POST'])
def confirmar():
    global status_script
    if "Executando" not in status_script:
        # Roda o script em uma thread separada para o Flask não travar a página web
        threading.Thread(target=minha_tarefa_pesada).start()
    return redirect(url_for('home'))

@app.route('/declinar', methods=['POST'])
def declinar():
    global status_script
    if "Executando" not in status_script:
        # Roda o script em uma thread separada para o Flask não travar a página web
        threading.Thread(target=dor).start()
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Roda o servidor aceitando conexões de qualquer IP da rede Tailscale na porta 5000
    app.run(host='0.0.0.0', port=5000)
