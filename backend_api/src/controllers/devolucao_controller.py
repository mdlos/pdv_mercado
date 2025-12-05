# src/controllers/devolucao_controller.py 

from flask import Blueprint, request, jsonify
from src.schemas.devolucao_schema import DevolucaoSchema
from src.models.devolucao_dao import DevolucaoDAO
from marshmallow import ValidationError
from http import HTTPStatus
import logging
from src.utils.formatters import clean_only_numbers 

logger = logging.getLogger(__name__)
devolucao_bp = Blueprint('devolucao', __name__, url_prefix='/api/v1/devolucoes')

devolucao_dao = DevolucaoDAO()
devolucao_schema = DevolucaoSchema()

# CPF DE TESTE
CPF_OPERADOR_LOGADO = "77788899901" 

@devolucao_bp.route('/', methods=['POST'])
def registrar_devolucao():
    """ Rota para registrar uma devolução e restaurar o estoque. """
    data = request.get_json()
    
    # Injeta o CPF do operador logado
    data['cpf_funcionario'] = CPF_OPERADOR_LOGADO 
    
    # VALIDAÇÃO
    try:
        validated_data = devolucao_schema.load(data) 
    except ValidationError as e:
        logger.error(f"Erro de validação na devolução: {e}")
        return jsonify({"message": "Erro de validação nos dados da devolução.", "errors": e.messages}), HTTPStatus.BAD_REQUEST
        
    # PROCESSO DE TRANSAÇÃO
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
        

@devolucao_bp.route('/credito', methods=['GET'])
def get_active_credit():
    """ 
    Busca e retorna todos os vales de crédito ATIVOS para o CPF do cliente. 
    A busca é feita via parâmetro de consulta (?cpf=...)
    """
    cpf_cliente = request.args.get('cpf')
    
    if not cpf_cliente:
        return jsonify({"message": "O CPF do cliente é obrigatório para esta busca."}), HTTPStatus.BAD_REQUEST

    cpf_limpo = clean_only_numbers(cpf_cliente)
    
    creditos = devolucao_dao.find_active_credit_by_cpf(cpf_limpo)
    
    if creditos:
        return jsonify(creditos), HTTPStatus.OK
    else:
        return jsonify({"message": f"Nenhum vale crédito ativo encontrado para o CPF {cpf_cliente}."}), HTTPStatus.NOT_FOUND


@devolucao_bp.route('/<int:id_devolucao>', methods=['GET'])
def get_devolucao_details_by_id(id_devolucao):
    """ Busca todos os detalhes da devolução (relatório de impressão) pelo ID. """
    
    devolucao_completa = devolucao_dao.buscar_devolucao_completa(id_devolucao)
    
    if devolucao_completa:
        return jsonify(devolucao_completa), HTTPStatus.OK
    else:
        return jsonify({"message": f"Devolução com ID {id_devolucao} não encontrada."}), HTTPStatus.NOT_FOUND


@devolucao_bp.route('/cliente', methods=['GET'])
def get_devolucao_details_by_cpf():
    """ 
    Busca a LISTA de todas as devoluções de um cliente para o operador escolher qual imprimir.
    A busca é feita via parâmetro de consulta (?cpf=...)
    """
    cpf_cliente = request.args.get('cpf')
    
    if not cpf_cliente:
        return jsonify({"message": "O CPF do cliente é obrigatório para esta busca."}), HTTPStatus.BAD_REQUEST
        
    cpf_limpo = clean_only_numbers(cpf_cliente)
    
    # Busca todos os IDs de devolução do cliente
    devolucoes_ids = devolucao_dao.find_devolucao_ids_by_cpf(cpf_limpo)
    
    if not devolucoes_ids:
        return jsonify({"message": f"Nenhuma devolução encontrada para o CPF {cpf_cliente}."}), HTTPStatus.NOT_FOUND

    devolucoes_completas = []
    
    # Para cada ID, busca o relatório completo
    for dev_id in devolucoes_ids:
        devolucao_completa = devolucao_dao.buscar_devolucao_completa(dev_id['id_devolucao'])
        if devolucao_completa:
            devolucoes_completas.append(devolucao_completa)
            
    return jsonify(devolucoes_completas), HTTPStatus.OK