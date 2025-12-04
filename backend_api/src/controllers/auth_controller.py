# src/controllers/auth_controller.py

from flask import Blueprint, request, jsonify
from app import bcrypt
from src.models.funcionario_dao import FuncionarioDAO
from src.security.jwt_auth import encode_auth_token # 🛑 NOVO: Importa o gerador de token
from http import HTTPStatus # 🛑 NOVO: Importa o HTTPStatus para clareza

auth_bp = Blueprint('auth', __name__)
dao = FuncionarioDAO()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    # Verifica se vieram todos os campos
    if not data or "email" not in data or "senha" not in data:
        return jsonify({"error": "Email e senha são obrigatórios"}), HTTPStatus.BAD_REQUEST # 400

    email = data["email"].strip()
    senha = data["senha"]

    funcionario = dao.find_by_email(email)

    if not funcionario:
        return jsonify({"error": "Funcionário não encontrado"}), HTTPStatus.NOT_FOUND # 404

    # Verificar senha com bcrypt
    # O campo correto para a senha no DAO é 'senha', não 'senha_hash' (conforme o DAO refatorado)
    if not bcrypt.check_password_hash(funcionario["senha"], senha):
        return jsonify({"error": "Senha incorreta"}), HTTPStatus.UNAUTHORIZED # 401

    # 🛑 PASSO CRÍTICO: Geração do Token JWT (após o login ser bem-sucedido)
    cargo_nome = funcionario.get("tipo_cargo", "Caixa") # Garante que o cargo seja retornado
    auth_token = encode_auth_token(funcionario["cpf"], cargo_nome)
    
    # Login ok
    return jsonify({
        "cpf": funcionario["cpf"],
        "nome": funcionario["nome"],
        "cargo": cargo_nome,
        "token": auth_token # 🛑 RETORNA O TOKEN PARA O FRONT-END USAR
    }), HTTPStatus.OK # 200