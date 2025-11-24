# src/controllers/devolucao_controller.py

from flask import Blueprint, request, jsonify
from src.schemas.devolucao_schema import DevolucaoSchema
from src.models.devolucao_dao import DevolucaoDAO
from marshmallow import ValidationError
from http import HTTPStatus
import logging

logger = logging.getLogger(__name__)
devolucao_bp = Blueprint('devolucao', __name__, url_prefix='/api/v1/devolucoes')

devolucao_dao = DevolucaoDAO()
devolucao_schema = DevolucaoSchema()

@devolucao_bp.route('/', methods=['POST'])
def registrar_devolucao():
    """ Rota para registrar uma devolução e restaurar o estoque. """
    data = request.get_json()
    
    # 1. VALIDAÇÃO
    try:
        validated_data = devolucao_schema.load(data) 
    except ValidationError as e:
        logger.error(f"Erro de validação na devolução: {e}")
        return jsonify({"message": "Erro de validação nos dados da devolução.", "errors": e.messages}), HTTPStatus.BAD_REQUEST
        
    # 2. PROCESSO DE TRANSAÇÃO (DAO)
    try:
        id_devolucao = devolucao_dao.registrar_devolucao(validated_data)
        
        if id_devolucao:
            return jsonify({
                "message": f"Devolução registrada com sucesso. Estoque restaurado.", 
                "id_devolucao": id_devolucao
            }), HTTPStatus.CREATED
        else:
            return jsonify({
                "message": "Falha na transação de devolução. Verifique o ID da venda.", 
                "status": "Error"
            }), HTTPStatus.INTERNAL_SERVER_ERROR
            
    except Exception as e:
        logger.error(f"Erro interno ao processar a devolução: {e}")
        return jsonify({
            "message": "Erro interno ao registrar a devolução. Transação desfeita.", 
            "status": "Error"
        }), HTTPStatus.INTERNAL_SERVER_ERROR

# Rotas de GET/DELETE (leitura de devolução) seriam implementadas aqui.