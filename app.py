from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    cnpj = "".join(filter(str.isdigit, request.form.get('cnpj', '')))
    fonte = request.form.get('fonte', '1') # 1 para CNPJA, 2 para ReceitaWS

    if len(cnpj) != 14:
        return jsonify({'status': 'ERROR', 'message': 'CNPJ inválido.'}), 400

    try:
        if fonte == '1':
            # Fonte: CNPJA
            url = f"https://open.cnpja.com/office/{cnpj}"
        else:
            # Fonte: ReceitaWS
            url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"

        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            # Padronização: A CNPJA tem campos diferentes (ex: 'company' em vez de 'nome')
            # Vamos ajustar para o front-end receber sempre o mesmo formato
            return jsonify(formatar_resposta(dados, fonte))
        
        return jsonify({'status': 'ERROR', 'message': f'Erro na API ({response.status_code})'}), response.status_code

    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': str(e)}), 500

def formatar_resposta(dados, fonte):
    """Padroniza a resposta das duas APIs para o front-end"""
    if fonte == '1': # CNPJA
        return {
            'nome': dados.get('company', {}).get('name'),
            'fantasia': dados.get('alias'),
            'cnpj': dados.get('taxId'),
            'situacao': dados.get('status', {}).get('text'),
            'abertura': dados.get('founded'),
            'email': dados.get('emails', [{}])[0].get('address') if dados.get('emails') else '',
            'telefone': dados.get('phones', [{}])[0].get('number') if dados.get('phones') else '',
            'logradouro': dados.get('address', {}).get('street'),
            'numero': dados.get('address', {}).get('number'),
            'bairro': dados.get('address', {}).get('district'),
            'municipio': dados.get('address', {}).get('city'),
            'uf': dados.get('address', {}).get('state'),
            'cep': dados.get('address', {}).get('zip'),
            'qsa': [{'nome': s.get('name'), 'qual': s.get('role', {}).get('text')} for s in dados.get('company', {}).get('members', [])]
        }
    return dados # ReceitaWS já vem no formato que usamos

if __name__ == '__main__':
    app.run(debug=True)