# src/controllers/compra_controller.py

from flask import Blueprint, request, jsonify
from src.schemas.compra_schema import CompraSchema
from src.models.compra_dao import CompraDAO
from marshmallow import ValidationError
from http import HTTPStatus
import logging

logger = logging.getLogger(__name__)
compra_bp = Blueprint('compra', __name__, url_prefix='/api/v1/compras')

compra_dao = CompraDAO()
compra_schema = CompraSchema() 

@compra_bp.route('/', methods=['POST'])
def registrar_compra():
    """ Rota para registrar uma nova compra e aumentar o estoque. """
    data = request.get_json()
    
    # 1. VALIDAÇÃO
    try:
        validated_data = compra_schema.load(data) 
    except ValidationError as e:
        logger.error(f"Erro de validação na compra: {e}")
        return jsonify({"message": "Erro de validação nos dados da compra.", "errors": e.messages}), HTTPStatus.BAD_REQUEST
        
    # 2. PROCESSO DE TRANSAÇÃO (DAO)
    try:
        id_compra = compra_dao.registrar_compra(validated_data)
        
        if id_compra:
            return jsonify({
                "message": "Compra registrada com sucesso. Estoque atualizado.", 
                "id_compra": id_compra
            }), HTTPStatus.CREATED
        else:
            return jsonify({
                "message": "Falha na transação de compra. Verifique o ID do fornecedor ou do produto.", 
                "status": "Error"
            }), HTTPStatus.INTERNAL_SERVER_ERROR
            
    except Exception as e:
        logger.error(f"Erro interno ao processar a compra: {e}")
        return jsonify({
            "message": "Erro interno ao registrar a compra. Transação desfeita.", 
            "status": "Error"
        }), HTTPStatus.INTERNAL_SERVER_ERROR