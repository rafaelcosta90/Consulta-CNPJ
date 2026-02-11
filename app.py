from flask import Flask, render_template, request, jsonify
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import threading # Para o site não travar enquanto o robô trabalha

app = Flask(__name__)

# Armazenamos os últimos dados consultados em memória para facilitar
dados_globais = {}

def rodar_automacao(dados):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get("https://www.lancefacil.com/Cadastro")
        driver.maximize_window()
        # Preenchimento
        driver.find_element(By.ID, "Cnpj").send_keys(dados.get('cnpj', ''))
        driver.find_element(By.ID, "RazaoSocial").send_keys(dados.get('nome', ''))
        driver.find_element(By.ID, "Email").send_keys(dados.get('email', ''))
        driver.find_element(By.ID, "ConfirmarEmail").send_keys(dados.get('email', ''))
        driver.find_element(By.ID, "Telefone").send_keys(dados.get('telefone', ''))
        driver.find_element(By.ID, "Celular").send_keys(dados.get('telefone', ''))
    except Exception as e:
        print(f"Erro na automação: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    global dados_globais
    cnpj = "".join(filter(str.isdigit, request.form.get('cnpj', '')))
    response = requests.get(f"https://receitaws.com.br/v1/cnpj/{cnpj}")
    dados_globais = response.json()
    return jsonify(dados_globais)

@app.route('/automar', methods=['POST'])
def automar():
    if not dados_globais:
        return jsonify({'erro': 'Consulte um CNPJ primeiro!'}), 400
    
    # Rodar em uma thread separada para o site não ficar "carregando" infinitamente
    threading.Thread(target=rodar_automacao, args=(dados_globais,)).start()
    return jsonify({'status': 'Robô iniciado!'})

if __name__ == '__main__':
    app.run(debug=True)