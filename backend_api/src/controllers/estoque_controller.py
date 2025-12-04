# src/controllers/estoque_controller.py

from flask import Blueprint, jsonify, request
from src.models.estoque_dao import EstoqueDAO
from src.schemas.estoque_schema import EstoqueSchema
from marshmallow import ValidationError
import http

estoque_bp = Blueprint('estoque', __name__)
estoque_dao = EstoqueDAO()
estoque_schema = EstoqueSchema()

# =======================================================
# 1. READ ONE (GET /api/v1/estoque/{id})
# =======================================================

@estoque_bp.route('/<int:codigo_produto>', methods=['GET'])
def get_estoque_by_product_id(codigo_produto):
    """ Retorna o estoque de um produto específico. """
    
    estoque_data = estoque_dao.find_by_product_id(codigo_produto)
    
    if estoque_data is None:
        return jsonify({"message": f"Estoque para o produto {codigo_produto} não encontrado."}), http.HTTPStatus.NOT_FOUND
    
    # Serializa e retorna
    result = estoque_schema.dump(estoque_data)
    return jsonify(result), http.HTTPStatus.OK

# =======================================================
# 2. UPDATE (PUT /api/v1/estoque/{id}) - Ajuste de Quantidade
# =======================================================

@estoque_bp.route('/<int:codigo_produto>', methods=['PUT'])
def update_estoque_quantity(codigo_produto):
    """ Rota para ajustar a quantidade de um produto no estoque. """
    data = request.get_json()
    
    # 1. VALIDAÇÃO
    try:
        # A validação precisa do codigo_produto e da quantidade
        data['codigo_produto'] = codigo_produto # Injeta o ID da URL para validação
        valid_data = estoque_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), http.HTTPStatus.BAD_REQUEST
    
    nova_quantidade = valid_data['quantidade']
    
    # 2. CHAMADA AO DAO
    rows_affected = estoque_dao.update_quantity(codigo_produto, nova_quantidade)
    
    # 3. RESPOSTA
    if rows_affected == 1:
        return jsonify({"message": f"Estoque do produto {codigo_produto} atualizado para {nova_quantidade}."}), http.HTTPStatus.OK
    elif rows_affected == 0:
        return jsonify({"message": f"Produto {codigo_produto} não encontrado no estoque."}), http.HTTPStatus.NOT_FOUND
    else:
        return jsonify({"message": "Falha na atualização de estoque (Erro interno).", "status": "Error"}), http.HTTPStatus.INTERNAL_SERVER_ERROR