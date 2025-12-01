# app.py (VERSÃO CORRIGIDA)

from flask import Flask, jsonify
from dotenv import load_dotenv
import os
from config import Config

# IMPORTS DE BLUEPRINTS SEM DEPENDÊNCIA DO BCRYPT
from src.controllers.cliente_controller import cliente_bp
from src.controllers.produto_controller import produto_bp
from src.controllers.estoque_controller import estoque_bp
from src.controllers.venda_controller import venda_bp
from src.controllers.devolucao_controller import devolucao_bp
from src.controllers.compra_controller import compra_bp
from src.controllers.tipo_funcionario_controller import tipo_funcionario_bp
from src.controllers.fornecedor_controller import fornecedor_bp
from src.controllers.fluxo_caixa_controller import fluxo_caixa_bp

# Bcrypt 
from flask_bcrypt import Bcrypt

# Serviço que cria admin inicial
from src.services.admin_setup_service import initialize_application

# Carrega variáveis do arquivo .env
load_dotenv()

# Instância global do Bcrypt
bcrypt = Bcrypt()


# 🛑 CORREÇÃO: Adicionamos 'testing=False' como argumento padrão
def create_app(testing=False):
    # Inicializa instância do Flask
    app = Flask(__name__)

    # Carrega configurações da classe Config
    app.config.from_object(Config)

    # 🛑 CORREÇÃO: Define a flag TESTING ANTES de inicializar o Bcrypt e chamar o setup
    if testing:
        app.config["TESTING"] = True

    # Inicializa o Bcrypt vinculado ao app
    bcrypt.init_app(app)

    # -----------------------------------------------------------
    # ROTINA AUTOMÁTICA PARA CRIAR ADMIN (caso não exista)
    # -----------------------------------------------------------
    with app.app_context():
        # initialize_application usará app.config.get("TESTING")
        initialize_application(app, bcrypt) 

    # ================================================
    # IMPORT LOCAL PARA QUEBRAR CICLO (bcrypt → auth)
    # ================================================
    from src.controllers.funcionario_controller import funcionario_bp
    from src.controllers.auth_controller import auth_bp

    # -----------------------------------------------------------
    # REGISTRO DE BLUEPRINTS
    # -----------------------------------------------------------

    # Autenticação
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    # Cadastros básicos
    app.register_blueprint(cliente_bp, url_prefix='/api/v1/clientes')
    app.register_blueprint(fornecedor_bp, url_prefix='/api/v1/fornecedores')
    app.register_blueprint(produto_bp, url_prefix='/api/v1/produtos')
    app.register_blueprint(estoque_bp, url_prefix='/api/v1/estoque')

    # Funcionários e Tipos
    app.register_blueprint(funcionario_bp, url_prefix='/api/v1/funcionarios')
    app.register_blueprint(tipo_funcionario_bp, url_prefix='/api/v1/tipos-funcionario')

    # Transações do PDV
    app.register_blueprint(compra_bp, url_prefix='/api/v1/compras')
    app.register_blueprint(venda_bp, url_prefix='/api/v1/vendas')
    app.register_blueprint(devolucao_bp, url_prefix='/api/v1/devolucoes')
    app.register_blueprint(fluxo_caixa_bp, url_prefix='/api/v1/fluxo-caixa')

    # -----------------------------------------------------------
    # ROTA RAIZ PARA VERIFICAR SE A API ESTÁ NO AR
    # -----------------------------------------------------------
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"message": "API Rodando! Versão: v1"})

    return app


# Executa a aplicação
if __name__ == '__main__':
    port = os.getenv('PORT', 5000)
    # 🛑 Ajuste aqui: create_app() agora pode ser chamado sem argumentos
    app = create_app() 
    app.run(debug=True, port=port)