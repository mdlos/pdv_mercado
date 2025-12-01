from flask import Blueprint, request, jsonify
from app import bcrypt
from src.models.funcionario_dao import FuncionarioDAO

auth_bp = Blueprint('auth', __name__)
dao = FuncionarioDAO()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    # Verifica se vieram todos os campos
    if not data or "email" not in data or "senha" not in data:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    email = data["email"].strip()
    senha = data["senha"]

    funcionario = dao.find_by_email(email)

    if not funcionario:
        return jsonify({"error": "Funcionário não encontrado"}), 404

    # Verificar senha com bcrypt
    # NOTA: O campo correto para a senha no DAO é 'senha', não 'senha_hash' (conforme o DAO refatorado)
    if not bcrypt.check_password_hash(funcionario["senha"], senha):
        return jsonify({"error": "Senha incorreta"}), 401

    # Login ok
    return jsonify({
        "cpf": funcionario["cpf"], # Usando CPF como ID principal
        "nome": funcionario["nome"],
        "email": funcionario["email"],
        "cargo": funcionario["tipo_cargo"] # Usando o campo 'tipo_cargo' retornado pelo JOIN no DAO
    }), 200