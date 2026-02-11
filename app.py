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
    elif fonte == '1':  # Ajuste específico para a estrutura da CNPJA enviada
        return {
            'nome': d.get('company', {}).get('name'),
            'fantasia': d.get('alias'),
            'cnpj': d.get('taxId'),
            'situacao': d.get('status', {}).get('text'),
            'abertura': d.get('founded'),
            'email': d.get('emails', [{}])[0].get('address') if d.get('emails') else '',
            'telefone': f"({d.get('phones', [{}])[0].get('area')}) {d.get('phones', [{}])[0].get('number')}" if d.get('phones') else '',
            'logradouro': d.get('address', {}).get('street'),
            'numero': d.get('address', {}).get('number'),
            'complemento': d.get('address', {}).get('details'),
            'bairro': d.get('address', {}).get('district'),
            'municipio': d.get('address', {}).get('city'),
            'uf': d.get('address', {}).get('state'),
            'cep': d.get('address', {}).get('zip'),
            # Novo mapeamento para buscar o nome dentro de person -> name
            'qsa': [
                {
                    'nome': s.get('person', {}).get('name'), 
                    'qual': s.get('role', {}).get('text')
                } for s in d.get('company', {}).get('members', [])
            ]
        }
    return dados # ReceitaWS já vem no formato que usamos

if __name__ == '__main__':
    app.run(debug=True)