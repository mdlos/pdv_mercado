# src/controllers/venda_controller.py

from flask import Blueprint, request, jsonify
import logging
from src.schemas.venda_schema import VendaSchema
from src.models.venda_dao import VendaDAO
from marshmallow import ValidationError
from http import HTTPStatus
from datetime import date 
from src.utils.formatters import clean_only_numbers 

# Instanciação dos objetos globais
venda_dao = VendaDAO() 
venda_schema = VendaSchema() 

venda_bp = Blueprint('venda', __name__, url_prefix='/api/v1/vendas')
logger = logging.getLogger(__name__)

# -----------------------------------------------------------
# C - CREATE (POST /) -  ROTA ADICIONADA
# -----------------------------------------------------------
@venda_bp.route('/', methods=['POST'], strict_slashes=False)
def criar_venda():
    """ Rota para registrar uma nova venda completa. """
    data = request.get_json()
    
    # 1. VALIDAÇÃO
    try:
        validated_data = venda_schema.load(data) 
    except ValidationError as e:
        logger.error(f"Erro de validação ao criar venda: {e}")
        return jsonify({"message": "Erro de validação nos dados da venda.", "errors": e.messages}), HTTPStatus.BAD_REQUEST
        
    # 2. PROCESSO DE TRANSAÇÃO (DAO)
    try:
        id_venda = venda_dao.registrar_venda(validated_data) # CHAMA O DAO
        
        if id_venda:
            # CORREÇÃO: Busca o registro completo para retornar Troco/Total
            venda_completa = venda_dao.buscar_por_id(id_venda) 
            
            return venda_schema.dump(venda_completa), HTTPStatus.CREATED 
        else:
            return jsonify({
                "message": "Falha na transação de venda. Motivo: Estoque insuficiente, dados duplicados ou erro de FK.", 
                "status": "Error"
            }), HTTPStatus.INTERNAL_SERVER_ERROR
            
    except Exception as e:
        logger.error(f"Erro interno ao processar a venda: {e}")
        return jsonify({
            "message": "Erro interno ao registrar a venda. Transação desfeita.", 
            "status": "Error"
        }), HTTPStatus.INTERNAL_SERVER_ERROR
        
# -----------------------------------------------------------
# R - READ (Busca por ID / Número da Nota) - JÁ FUNCIONA
# -----------------------------------------------------------
@venda_bp.route('/<int:id_venda>', methods=['GET'])
def get_venda_by_id(id_venda):
    """ Rota para buscar uma venda e seus detalhes (por número da nota). """
    
    venda_data = venda_dao.buscar_por_id(id_venda)
    
    if venda_data:
        return venda_schema.dump(venda_data), HTTPStatus.OK
    else:
        return jsonify({"message": f"Venda com ID {id_venda} não encontrada."}), HTTPStatus.NOT_FOUND

# -----------------------------------------------------------
# R - READ ALL / BUSCA FLEXÍVEL (Tudo, por Data, ou por CPF)
# -----------------------------------------------------------
@venda_bp.route('/', methods=['GET'], strict_slashes=False)
@venda_bp.route('/hoje', methods=['GET'])
@venda_bp.route('/busca', methods=['GET'])
def get_vendas_flexivel():
    """ 
    Rota unificada para listagem e filtro:
    - GET /api/v1/vendas/           -> Lista todas as vendas (se existirem).
    - GET /api/v1/vendas/?data=...  -> Filtra por data.
    - GET /api/v1/vendas/hoje       -> Filtra pela data de hoje.
    """
    
    data_str = request.args.get('data')
    cpf_cliente = request.args.get('cpf')
    
    # 1. Trata a rota /hoje para definir a data de hoje
    if request.path.endswith('/hoje'):
        data_str = date.today().isoformat()
        
    # 2. Prepara o filtro de CPF (limpando o valor)
    filter_cpf = None
    if cpf_cliente:
        filter_cpf = clean_only_numbers(cpf_cliente)
        
    # 3. Executa a busca (passa None se o filtro não foi fornecido)
    vendas_data = venda_dao.buscar_vendas_flexivel(
        data_str=data_str,  # Será 'None' (Listar Tudo) ou 'YYYY-MM-DD'
        cpf_cliente=filter_cpf # Será 'None' (Listar Tudo) ou CPF limpo
    )

    # 4. Serialização e Resposta
    if vendas_data:
        return venda_schema.dump(vendas_data, many=True), HTTPStatus.OK
    
    # Retorna lista vazia em vez de 404 para evitar erro no frontend
    return jsonify([]), HTTPStatus.OK