# app.py (CORREÇÃO FINAL DE IMPORTAÇÃO CIRCULAR)

from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from config import Config
from src.controllers.cliente_controller import cliente_bp 
from src.controllers.produto_controller import produto_bp 
from src.controllers.estoque_controller import estoque_bp 
from src.controllers.venda_controller import venda_bp 
from src.controllers.devolucao_controller import devolucao_bp 
from src.controllers.compra_controller import compra_bp 
from src.controllers.tipo_funcionario_controller import tipo_funcionario_bp 
from src.controllers.fornecedor_controller import fornecedor_bp 
from src.controllers.fluxo_caixa_controller import fluxo_caixa_bp 

from flask_bcrypt import Bcrypt 
from src.services.admin_setup_service import initialize_application 

# Carrega as variáveis do .env no ambiente antes de tudo
load_dotenv()

# Define o objeto Bcrypt globalmente
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
        initialize_application(app, bcrypt) 
        
    # --- REGISTRO DE BLUEPRINTS (AGORA COM O IMPORT LOCAL DE FUNCIONÁRIO) ---
    # 🔑 QUEBRA DO CICLO: Importa o funcionario_bp AQUI dentro, onde 'bcrypt' já está inicializado.
    from src.controllers.funcionario_controller import funcionario_bp 
    
    # Módulos de Cadastro Base
    app.register_blueprint(cliente_bp, url_prefix='/api/v1/clientes') 
    app.register_blueprint(fornecedor_bp, url_prefix='/api/v1/fornecedores')
    app.register_blueprint(produto_bp, url_prefix='/api/v1/produtos')
    app.register_blueprint(estoque_bp, url_prefix='/api/v1/estoque')
    
    # Módulos de Funcionário/Catálogo
    app.register_blueprint(funcionario_bp, url_prefix='/api/v1/funcionarios') 
    app.register_blueprint(tipo_funcionario_bp, url_prefix='/api/v1/tipos-funcionario')
    
    # Módulos de Transação/PDV
    app.register_blueprint(compra_bp, url_prefix='/api/v1/compras')
    app.register_blueprint(venda_bp, url_prefix='/api/v1/vendas')
    app.register_blueprint(devolucao_bp, url_prefix='/api/v1/devolucoes')
    app.register_blueprint(fluxo_caixa_bp, url_prefix='/api/v1/fluxo-caixa') 
    
    
    # Rota de teste simples para verificar se o Flask está rodando
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"message": "API Rodando! Versão: v1"})

    return app

if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    app = create_app()
    app.run(debug=True, port=port)