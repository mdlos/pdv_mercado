# app.py

from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from config import Config
from src.controllers.cliente_controller import cliente_bp # NOVO IMPORT AQUI!

# Carrega as variáveis do .env no ambiente antes de tudo
load_dotenv()

def create_app():
    # Inicializa a aplicação Flask
    app = Flask(__name__)

    # Carrega as configurações
    app.config.from_object(Config)

    # --- Registro de Blueprints (Controllers) ---
    # Registra o Controller do Cliente com o prefixo da URL da API
    app.register_blueprint(cliente_bp, url_prefix='/api/v1/clientes') 
    
    # Rota de teste simples para verificar se o Flask está rodando
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"message": "API Rodando! Versão: v1"})

    return app

if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    app = create_app()
    app.run(debug=True, port=port)