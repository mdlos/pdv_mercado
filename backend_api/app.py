# app.py

from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from config import Config
from src.controllers.cliente_controller import cliente_bp 
from src.controllers.produto_controller import produto_bp 
from src.controllers.estoque_controller import estoque_bp 
from flask_bcrypt import Bcrypt 
from src.services.admin_setup_service import initialize_application 
from src.controllers.tipo_funcionario_controller import tipo_funcionario_bp # NOVO IMPORT

# Carrega as variáveis do .env no ambiente antes de tudo
load_dotenv()

# Define o objeto Bcrypt globalmente (mas não o inicializa)
bcrypt = Bcrypt() 

def create_app():
    # Inicializa a aplicação Flask
    app = Flask(__name__)

    # Carrega as configurações
    app.config.from_object(Config)
    
    # 1. Inicializa o Bcrypt e o liga à aplicação Flask
    bcrypt.init_app(app) 

    # ---------------------------------------------------------------
    # 2. Rotina de Inicialização e Criação do Admin
    # ---------------------------------------------------------------
    with app.app_context():
        # Passa o objeto bcrypt para o serviço de setup
        initialize_application(app, bcrypt) 
        
    # --- Registro de Blueprints (Controllers) ---
    from src.controllers.funcionario_controller import funcionario_bp 
    
    app.register_blueprint(cliente_bp, url_prefix='/api/v1/clientes') 
    app.register_blueprint(produto_bp, url_prefix='/api/v1/produtos')
    app.register_blueprint(estoque_bp, url_prefix='/api/v1/estoque')
    app.register_blueprint(funcionario_bp, url_prefix='/api/v1/funcionarios') 
    
    # NOVO REGISTRO: Rota para buscar os cargos
    app.register_blueprint(tipo_funcionario_bp, url_prefix='/api/v1/tipos-funcionario')
    
    
    # Rota de teste simples para verificar se o Flask está rodando
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"message": "API Rodando! Versão: v1"})

    return app

if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    app = create_app()
    app.run(debug=True, port=port)