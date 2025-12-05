# src/controllers/compra_controller.py 

from flask import Blueprint, request, jsonify
from src.schemas.compra_schema import CompraSchema
from src.models.compra_dao import CompraDAO
from marshmallow import ValidationError
from http import HTTPStatus
import logging

logger = logging.getLogger(__name__)

# Instanciação dos objetos globais
compra_dao = CompraDAO()
compra_schema = CompraSchema() 
compras_schema_many = CompraSchema(many=True)
compra_bp = Blueprint('compra', __name__, url_prefix='/api/v1/compras')


@compra_bp.route('/', methods=['POST'])
def registrar_compra():
    """ Rota para registrar uma nova compra e aumentar o estoque. """
    data = request.get_json()
    
    # VALIDAÇÃO
    try:
        validated_data = compra_schema.load(data) 
    except ValidationError as e:
        logger.error(f"Erro de validação na compra: {e}")
        return jsonify({"message": "Erro de validação nos dados da compra.", "errors": e.messages}), HTTPStatus.BAD_REQUEST
        
    # PROCESSO DE TRANSAÇÃO
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


@compra_bp.route('/', methods=['GET'])
@compra_bp.route('/periodo', methods=['GET'])
def get_compras_flexivel():
    """ 
    Rota para listar todas as compras ou filtrar por período de data.
    Ex: /compras/?inicio=2025-11-01&fim=2025-11-30
    """
    
    # Captura os parâmetros de data
    data_inicio = request.args.get('inicio')
    data_fim = request.args.get('fim')
    
    # Busca no DAO
    compras = compra_dao.find_by_date(
        data_inicio=data_inicio, 
        data_fim=data_fim
    )
    
    # Serialização e Resposta
    if compras:
        return compras_schema_many.dump(compras), HTTPStatus.OK
    
    # Tratamento de Not Found
    if data_inicio or data_fim:
        return jsonify({"message": "Nenhuma compra encontrada no período especificado."}), HTTPStatus.NOT_FOUND
    else:
        return jsonify({"message": "Nenhuma compra registrada no sistema."}), HTTPStatus.NOT_FOUND