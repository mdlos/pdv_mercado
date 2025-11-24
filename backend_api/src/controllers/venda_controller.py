# src/controllers/venda_controller.py (Ajuste Final)

from flask import Blueprint, request, jsonify
import logging
from src.schemas.venda_schema import VendaSchema
from src.models.venda_dao import VendaDAO # NOVO IMPORT

venda_bp = Blueprint('venda', __name__, url_prefix='/api/v1/vendas')
logger = logging.getLogger(__name__)

venda_schema = VendaSchema() 
venda_dao = VendaDAO() # Instancia o DAO

@venda_bp.route('/', methods=['POST'])
def criar_venda():
    """ Rota para registrar uma nova venda completa. """
    data = request.get_json()
    
    # 1. VALIDAÇÃO
    try:
        validated_data = venda_schema.load(data) 
    except Exception as e:
        logger.error(f"Erro de validação ao criar venda: {e}")
        return jsonify({"message": "Erro de validação nos dados da venda.", "errors": str(e)}), 400
        
    # 2. PROCESSO DE TRANSAÇÃO (DAO)
    try:
        id_venda = venda_dao.registrar_venda(validated_data) # CHAMA O DAO
        
        if id_venda:
            return jsonify({
                "message": f"Venda registrada com sucesso.", 
                "id_venda": id_venda,
                "status": "Success"
            }), 201
        else:
            return jsonify({
                "message": "Falha na transação de venda. Motivo: Estoque insuficiente, dados duplicados ou erro de FK.", 
                "status": "Error"
            }), 500
            
    except Exception as e:
        logger.error(f"Erro interno ao processar a venda: {e}")
        return jsonify({
            "message": "Erro interno ao registrar a venda. Transação desfeita.", 
            "status": "Error"
        }), 500