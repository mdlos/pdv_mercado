# src/controllers/cliente_controller.py

from flask import Blueprint, jsonify, request
from src.models.cliente_dao import ClienteDAO
from src.schemas.cliente_schema import ClienteSchema
from marshmallow import ValidationError
import http

# Instanciação
cliente_bp = Blueprint('clientes', __name__)
cliente_dao = ClienteDAO()
cliente_schema = ClienteSchema()        # Para um único objeto (POST, PUT)
clientes_schema = ClienteSchema(many=True) # Para listas (GET)

# =======================================================
# 1. READ ALL & CREATE (GET /api/v1/clientes & POST /api/v1/clientes)
# =======================================================

@cliente_bp.route('/', methods=['GET'])
def get_clientes():
    """ Rota para listar todos os clientes (READ ALL). """
    clientes_data = cliente_dao.find_all()
    
    if clientes_data is not None:
        result = clientes_schema.dump(clientes_data) 
        return jsonify(result), http.HTTPStatus.OK
    else:
        return jsonify({"message": "Erro ao buscar clientes."}), http.HTTPStatus.INTERNAL_SERVER_ERROR
@cliente_bp.route('/', methods=['POST'])
def create_cliente():
    """ Rota para criar um novo cliente (CREATE) com validação e localização. """
    
    data = request.get_json()
    
    try:
        valid_data = cliente_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), http.HTTPStatus.BAD_REQUEST

    # 1. EXTRAÇÃO DOS DADOS (Cliente e Localização)
    cpf_cnpj = valid_data['cpf_cnpj']
    nome = valid_data['nome']
    
    # Extraindo telefone e sexo
    telefone = valid_data.get('telefone')
    sexo = valid_data.get('sexo')
    
    email = valid_data.get('email')
    localizacao_data = valid_data['localizacao']
    
    # 2. CHAMADA AO DAO (SQL PURO)
    # Passando telefone e sexo para o DAO
    new_id = cliente_dao.insert(cpf_cnpj, nome, email, telefone, sexo, localizacao_data)
    
    # 3. RESPOSTA
    if new_id:
        return jsonify({
            "message": "Cliente criado com sucesso!",
            "id_cliente": new_id,
            "nome": nome
        }), http.HTTPStatus.CREATED
    else:
        return jsonify({"message": "Falha ao criar cliente (Erro DB ou conflito de dados).", "status": "Error"}), http.HTTPStatus.INTERNAL_SERVER_ERROR
# =======================================================
# 2. READ ONE (GET /api/v1/clientes/{id})
# =======================================================

@cliente_bp.route('/<int:cliente_id>', methods=['GET'])
def get_cliente_by_id(cliente_id):
    """ Rota para buscar um cliente pelo ID (READ ONE). """
    
    cliente_data = cliente_dao.find_by_id(cliente_id)
    
    if cliente_data is None:
        return jsonify({"message": f"Cliente com ID {cliente_id} não encontrado."}), http.HTTPStatus.NOT_FOUND # 404
    
    # Serializa e retorna
    result = cliente_schema.dump(cliente_data)
    return jsonify(result), http.HTTPStatus.OK


# =======================================================
# 3. UPDATE (PUT /api/v1/clientes/{id})
# =======================================================
@cliente_bp.route('/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    """ Rota para atualizar um cliente existente (UPDATE). """
    data = request.get_json()
    
    # 1. VALIDAÇÃO (partial=True permite que campos sejam omitidos)
    try:
        valid_data = cliente_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), http.HTTPStatus.BAD_REQUEST

    # 2. SEPARAÇÃO DOS DADOS
    # Dados de Cliente
    nome = valid_data.get('nome')
    email = valid_data.get('email')
    cpf_cnpj = valid_data.get('cpf_cnpj')
    telefone = valid_data.get('telefone')
    sexo = valid_data.get('sexo')
    
    # Dados de Localização (Se o objeto 'localizacao' foi enviado)
    localizacao_data = valid_data.get('localizacao')

    # Se a requisição veio, mas não tinha NENHUM dado para atualizar
    if not any([nome, email, cpf_cnpj, telefone, sexo, localizacao_data]):
        return jsonify({"message": "Nenhum dado válido fornecido para atualização."}), http.HTTPStatus.BAD_REQUEST

    # 3. CHAMADA AO DAO
    rows_affected = cliente_dao.update(
        cliente_id=cliente_id,
        nome=nome,
        email=email,
        cpf_cnpj=cpf_cnpj,
        telefone=telefone,
        sexo=sexo,        
        localizacao_data=localizacao_data
    )

    # 4. RESPOSTA
    if rows_affected == 1:
        return jsonify({"message": f"Cliente {cliente_id} atualizado com sucesso!"}), http.HTTPStatus.OK
    elif rows_affected == 0:
        return jsonify({"message": f"Cliente {cliente_id} encontrado, mas nenhum dado foi alterado."}), http.HTTPStatus.OK
    else: # rows_affected == -1 (Erro de DB)
        return jsonify({"message": "Falha na atualização (Erro interno ou conflito de dados).", "status": "Error"}), http.HTTPStatus.INTERNAL_SERVER_ERROR

# =======================================================
# 4. DELETE (DELETE /api/v1/clientes/{id})
# =======================================================

@cliente_bp.route('/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    """ Rota para deletar um cliente (DELETE). """
    
    # 1. CHAMADA AO DAO (SQL PURO)
    rows_affected = cliente_dao.delete(cliente_id)
    
    # 2. RESPOSTA
    if rows_affected == 1:
        # 204 No Content é o padrão para DELETE bem-sucedido
        return '', http.HTTPStatus.NO_CONTENT 
    elif rows_affected == 0:
        return jsonify({"message": f"Cliente com ID {cliente_id} não encontrado."}), http.HTTPStatus.NOT_FOUND
    else: # rows_affected == -1 (Erro de DB)
        return jsonify({"message": "Falha na exclusão (Erro interno).", "status": "Error"}), http.HTTPStatus.INTERNAL_SERVER_ERROR