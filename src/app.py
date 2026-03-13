import os
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import re
import unicodedata

app = Flask(__name__, static_folder='../public', static_url_path='')
CORS(app)

# Lista de palavras ofensivas e racialmente depreciativas
PALAVRAS_OFENSIVAS = [
    'preto', 'preta', 'pretinho', 'pretinha', 'macaco', 'macaca', 'mono', 'mona',
    'negro', 'negra', 'neguinho', 'neguinha', 'morena', 'moreno', 'babaca',
    'idiot', 'burro', 'burra', 'vagabund', 'porra', 'caralh', 'puta', 'merda',
    'desgraç', 'filho da puta', 'fud', 'foder', 'cu', 'buceta', 'pica',
    'rola', 'pau', 'bicho', 'viad', 'bicha', 'traveco', 'sapatão',
    'otario', 'otaria', 'corno', 'corn', 'pilantr', 'ladrão', 'ladra',
    'fascist', 'nazist', 'racist', 'xenofob', 'homofob', 'transfob'
]

def contem_palavra_ofensiva(nome):
    """
    Verifica se o nome contém palavras ofensivas ou racialmente depreciativas
    """
    if not nome:
        return False
    
    # Converter para minúsculas e remover acentos
    nome_lower = nome.lower()
    nome_sem_acentos = unicodedata.normalize('NFD', nome_lower).encode('ascii', 'ignore').decode('utf-8')
    nome_sem_espacos = nome_sem_acentos.replace(' ', '')
    
    for palavra in PALAVRAS_OFENSIVAS:
        # Verifica palavra exata ou como substring
        if (palavra in nome_lower or 
            palavra in nome_sem_acentos or 
            palavra in nome_sem_espacos):
            return True
    
    return False

# Rota raiz redireciona para login.html
@app.route('/')
def root():
    return redirect('/login.html')

# Armazenamento temporário em memória para as remessas
remessas = []

@app.route('/api/remessas', methods=['GET'])
def listar_remessas():
    return jsonify(remessas)

@app.route('/api/remessas', methods=['POST'])
def adicionar_remessa():
    data = request.json
    numero = data.get('numero')
    operador = data.get('operador', 'Não identificado')
    
    if not numero:
        return jsonify({"error": "Número da remessa é obrigatório"}), 400
    
    # Validar se o nome do operador contém palavras ofensivas
    if contem_palavra_ofensiva(operador):
        return jsonify({"error": "Nome do operador não permitido. Por favor, use um nome apropriado."}), 400
    
    # Adicionar a remessa à lista com nome do operador
    remessas.append({
        'numero': numero,
        'operador': operador,
        'timestamp': __import__('datetime').datetime.now().strftime('%H:%M:%S')
    })
    return jsonify({"message": "Remessa adicionada com sucesso", "remessas": remessas}), 201

@app.route('/api/remessas/<int:index>', methods=['DELETE'])
def remover_remessa(index):
    try:
        if 0 <= index < len(remessas):
            removida = remessas.pop(index)
            return jsonify({"message": f"Remessa {removida['numero']} removida", "remessas": remessas})
        return jsonify({"error": "Índice inválido"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # O Railway obriga o uso da variável de ambiente PORT
    port = int(os.environ.get("PORT", 8027))
    # O host deve ser 0.0.0.0 para aceitar conexões externas
    app.run(host="0.0.0.0", port=port)
