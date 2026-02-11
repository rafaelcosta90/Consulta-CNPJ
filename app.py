from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    # 1. Captura e limpa os dados da requisição
    cnpj_bruto = request.form.get('cnpj', '')
    cnpj = "".join(filter(str.isdigit, cnpj_bruto))
    fonte = request.form.get('fonte', '3') # Padrão: BrasilAPI

    if len(cnpj) != 14:
        return jsonify({'status': 'ERROR', 'message': 'CNPJ deve ter 14 números.'}), 400

    try:
        # 2. Define a URL de acordo com a fonte selecionada
        if fonte == '1':
            url = f"https://open.cnpja.com/office/{cnpj}"
        elif fonte == '3':
            url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
        else:
            url = f"https://receitaws.com.br/v1/cnpj/{cnpj}"

        # 3. Faz a chamada para a API externa
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            dados_brutos = response.json()
            # 4. Padroniza a resposta para o formato que o HTML espera
            dados_final = padronizar_dados(dados_brutos, fonte)
            return jsonify(dados_final)
        
        elif response.status_code == 429:
            return jsonify({'status': 'ERROR', 'message': 'Muitas consultas! Tente outra fonte.'}), 429
        
        return jsonify({'status': 'ERROR', 'message': f'Erro na API (Status {response.status_code})'}), 500

    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': f'Falha na conexão: {str(e)}'}), 500

def padronizar_dados(d, fonte):
    """
    Padroniza as diferentes estruturas das APIs (BrasilAPI, CNPJA e ReceitaWS)
    em um único formato para o front-end.
    """
    
    # --- PADRONIZAÇÃO BRASILAPI (Fonte 3) ---
    if fonte == '3':
        return {
            'nome': d.get('razao_social'),
            'fantasia': d.get('nome_fantasia'),
            'cnpj': d.get('cnpj'),
            'situacao': d.get('descricao_situacao_cadastral'),
            'abertura': d.get('data_inicio_activity'),
            'email': d.get('email'),
            'telefone': f"({d.get('ddd_telefone_1', '')[:2]}) {d.get('ddd_telefone_1', '')[2:]}" if d.get('ddd_telefone_1') else '',
            'logradouro': d.get('logradouro'),
            'numero': d.get('numero'),
            'complemento': d.get('complemento'),
            'bairro': d.get('bairro'),
            'municipio': d.get('municipio'),
            'uf': d.get('uf'),
            'cep': d.get('cep'),
            'qsa': [{'nome': s.get('nome_socio'), 'qual': s.get('qualificacao_socio')} for s in d.get('qsa', [])]
        }
    
    # --- PADRONIZAÇÃO OPEN CNPJA (Fonte 1) ---
    elif fonte == '1':
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
            # Ajuste crucial: Entrando em company -> members -> person -> name
            'qsa': [
                {
                    'nome': s.get('person', {}).get('name'), 
                    'qual': s.get('role', {}).get('text')
                } for s in d.get('company', {}).get('members', [])
            ]
        }

    # --- PADRONIZAÇÃO RECEITAWS (Fonte 2) ---
    # O ReceitaWS já é o padrão base, retornamos o JSON como está
    return d

if __name__ == '__main__':
    app.run(debug=True)