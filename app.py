from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    cnpj = "".join(filter(str.isdigit, request.form.get('cnpj', '')))
    
    if len(cnpj) != 14:
        return jsonify({'erro': 'CNPJ deve conter 14 números.'}), 400

    try:
        response = requests.get(f"https://receitaws.com.br/v1/cnpj/{cnpj}", timeout=10)
        if response.status_code == 200:
            dados = response.json()
            if dados.get('status') == 'ERROR':
                return jsonify({'erro': dados.get('message')}), 400
            return jsonify(dados)
        elif response.status_code == 429:
            return jsonify({'erro': 'Limite de requisições atingido. Tente em 1 minuto.'}), 429
        return jsonify({'erro': 'Erro ao conectar na API.'}), 500
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)