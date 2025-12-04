# src/controllers/produto_controller.py

from flask import Blueprint, jsonify, request
from src.models.produto_dao import ProdutoDAO
from src.schemas.produto_schema import ProdutoSchema
from marshmallow import ValidationError
import http

# Instanciação
produto_bp = Blueprint('produtos', __name__)
produto_dao = ProdutoDAO()
produto_schema = ProdutoSchema()         # Para um único objeto (POST, PUT)
produtos_schema = ProdutoSchema(many=True) # Para listas (GET)

# =======================================================
# 1. READ ALL & CREATE (GET /api/v1/produtos & POST /api/v1/produtos)
# =======================================================

@produto_bp.route('/', methods=['GET'], strict_slashes=False)
def get_produtos():
    """ Rota para listar todos os produtos (READ ALL). """
    produtos_data = produto_dao.find_all()
    
    if produtos_data is not None:
        result = produtos_schema.dump(produtos_data) 
        return jsonify(result), http.HTTPStatus.OK
    else:
        return jsonify({"message": "Erro ao buscar produtos."}), http.HTTPStatus.INTERNAL_SERVER_ERROR

@produto_bp.route('/', methods=['POST'], strict_slashes=False)
def create_produto():
    """ Rota para criar um novo produto (CREATE), incluindo estoque inicial. """
    data = request.get_json()
    
    # 1. VALIDAÇÃO com Marshmallow
    try:
        valid_data = produto_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), http.HTTPStatus.BAD_REQUEST

    # 2. CHAMADA AO DAO (SQL PURO)
    nome = valid_data['nome']
    descricao = valid_data['descricao']
    preco = valid_data['preco']
    codigo_barras = valid_data.get('codigo_barras')
    
    # NOVO: Extrai a quantidade inicial (valor padrão será 0 se não for enviado)
    initial_quantity = valid_data.get('initial_quantity') 
    
    # Passa o valor da quantidade para o DAO
    codigo_produto = produto_dao.insert(
        nome, 
        descricao, 
        preco,
        codigo_barras,
        initial_quantity=initial_quantity # NOVO ARGUMENTO PASSADO
    )
    
    # 3. RESPOSTA
    if codigo_produto:
        return jsonify({
            "message": "Produto criado com sucesso!",
            "codigo_produto": codigo_produto,
            "nome": nome
        }), http.HTTPStatus.CREATED
    else:
        return jsonify({"message": "Falha ao criar produto (Erro interno ou DB).", "status": "Error"}), http.HTTPStatus.INTERNAL_SERVER_ERROR


# =======================================================
# 2. READ ONE (GET /api/v1/produtos/{id})
# =======================================================

@produto_bp.route('/<int:codigo_produto>', methods=['GET'])
def get_produto_by_id(codigo_produto):
    """ Rota para buscar um produto pelo código (READ ONE). """
    
    produto_data = produto_dao.find_by_id(codigo_produto)
    
    if produto_data is None:
        return jsonify({"message": f"Produto com código {codigo_produto} não encontrado."}), http.HTTPStatus.NOT_FOUND # 404
    
    result = produto_schema.dump(produto_data)
    return jsonify(result), http.HTTPStatus.OK


# =======================================================
# 3. UPDATE (PUT /api/v1/produtos/{id})
# =======================================================

@produto_bp.route('/<int:codigo_produto>', methods=['PUT'])
def update_produto(codigo_produto):
    """ Rota para atualizar um produto existente (UPDATE). """
    data = request.get_json()
    
    # 1. VALIDAÇÃO (partial=True permite a ausência de campos obrigatórios)
    try:
        # Note que initial_quantity NÃO é passado aqui, apenas os campos de produto
        valid_data = produto_schema.load(data, partial=True) 
    except ValidationError as err:
        return jsonify(err.messages), http.HTTPStatus.BAD_REQUEST

    if not valid_data:
        return jsonify({"message": "Nenhum dado válido fornecido para atualização."}), http.HTTPStatus.BAD_REQUEST

    # 2. CHAMADA AO DAO (SQL PURO)
    rows_affected = produto_dao.update(
        codigo_produto=codigo_produto,
        **valid_data 
    )

    # 3. RESPOSTA
    if rows_affected == 1:
        return jsonify({"message": f"Produto {codigo_produto} atualizado com sucesso!"}), http.HTTPStatus.OK
    elif rows_affected == 0:
        return jsonify({"message": f"Produto {codigo_produto} não encontrado ou nenhum dado novo para atualizar."}), http.HTTPStatus.NOT_FOUND
    else: 
        return jsonify({"message": "Falha na atualização (Erro interno ou DB).", "status": "Error"}), http.HTTPStatus.INTERNAL_SERVER_ERROR


# =======================================================
# 4. DELETE (DELETE /api/v1/produtos/{id})
# =======================================================

@produto_bp.route('/<int:codigo_produto>', methods=['DELETE'])
def delete_produto(codigo_produto):
    """ Rota para deletar um produto (DELETE). """
    
    # 1. CHAMADA AO DAO (SQL PURO)
    rows_affected = produto_dao.delete(codigo_produto)
    
    # 2. RESPOSTA
    if rows_affected == 1:
        return '', http.HTTPStatus.NO_CONTENT 
    elif rows_affected == 0:
        return jsonify({"message": f"Produto com código {codigo_produto} não encontrado."}), http.HTTPStatus.NOT_FOUND
    else: 
        return jsonify({"message": "Falha na exclusão (Erro interno).", "status": "Error"}), http.HTTPStatus.INTERNAL_SERVER_ERROR