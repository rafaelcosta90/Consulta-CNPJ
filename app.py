from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Configurações da API
API_URL = "https://receitaws.com.br/v1/cnpj/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    # Obtém o CNPJ enviado pelo front-end e limpa caracteres especiais
    cnpj_bruto = request.form.get('cnpj', '')
    cnpj = "".join(filter(str.isdigit, cnpj_bruto))
    
    if len(cnpj) != 14:
        return jsonify({'status': 'ERROR', 'message': 'O CNPJ deve conter exatamente 14 números.'}), 400

    try:
        # Faz a requisição para a API ReceitaWS
        response = requests.get(f"{API_URL}{cnpj}", timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            return jsonify(dados)
        
        elif response.status_code == 429:
            return jsonify({'status': 'ERROR', 'message': 'Limite de consultas atingido (3 por minuto).'}), 429
        
        else:
            return jsonify({'status': 'ERROR', 'message': f'Erro na API externa: {response.status_code}'}), 500
            
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': f'Erro interno no servidor: {str(e)}'}), 500

if __name__ == '__main__':
    # Em produção (Render), o Gunicorn usará o objeto 'app'
    app.run(debug=True)