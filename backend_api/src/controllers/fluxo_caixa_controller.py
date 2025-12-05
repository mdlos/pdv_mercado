# src/controllers/fluxo_caixa_controller.py 

from flask import Blueprint, request, jsonify
from src.schemas.fluxo_caixa_schema import FluxoCaixaSchema
from src.models.fluxo_caixa_dao import FluxoCaixaDAO
from marshmallow import ValidationError
from http import HTTPStatus
import logging
from decimal import Decimal
from src.services.fluxo_caixa_service import FluxoCaixaService 

logger = logging.getLogger(__name__)
fluxo_caixa_bp = Blueprint('fluxo_caixa', __name__, url_prefix='/api/v1/fluxo-caixa')

fluxo_caixa_dao = FluxoCaixaDAO()
fluxo_caixa_schema = FluxoCaixaSchema()
fluxo_caixa_service = FluxoCaixaService() 


@fluxo_caixa_bp.route('/abrir', methods=['POST'])
def abrir_caixa():
    """ Rota para abrir o turno de caixa. """
    data = request.get_json()
    
    # Validação
    try:
        validated_data = fluxo_caixa_schema.load(data) 
    except ValidationError as e:
        return jsonify({"message": "Erro de validação para abertura de caixa.", "errors": e.messages}), HTTPStatus.BAD_REQUEST
        
    cpf_funcionario = validated_data['cpf_funcionario']
    valor_inicial = validated_data['valor_inicial']
    
    # Verificaça se já existe um caixa aberto
    if fluxo_caixa_dao.buscar_caixa_aberto(cpf_funcionario):
        return jsonify({"message": "Já existe um turno de caixa aberto para este funcionário."}), HTTPStatus.CONFLICT # 409
        
    # CHAMADA AO DAO
    id_fluxo = fluxo_caixa_dao.abrir_caixa(cpf_funcionario, valor_inicial)
    if id_fluxo:
        return jsonify({
            "message": "Caixa aberto com sucesso.", 
            "id_fluxo": id_fluxo
        }), HTTPStatus.CREATED
    else:
        return jsonify({"message": "Falha ao abrir caixa. Verifique se o CPF é válido."}), HTTPStatus.INTERNAL_SERVER_ERROR


@fluxo_caixa_bp.route('/fechar/<string:cpf_funcionario>', methods=['PUT'])
def fechar_caixa(cpf_funcionario):
    """ 
    Rota para fechar o turno de caixa. O valor final é CALCULADO automaticamente.
    """
    
    # Busca o ID do turno aberto
    id_fluxo_aberto = fluxo_caixa_dao.buscar_caixa_aberto(cpf_funcionario)
    
    if not id_fluxo_aberto:
        return jsonify({"message": "Nenhum turno de caixa aberto encontrado para este funcionário."}), HTTPStatus.NOT_FOUND
        
    # Gera o resumo de fechamento
    resumo = fluxo_caixa_service.gerar_resumo_fechamento(id_fluxo_aberto)

    # Verifica se o Service falhou em gerar o resumo
    if resumo is None:
        return jsonify({"message": "Falha ao gerar o resumo de auditoria. Verifique os dados do fluxo."}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    # Extrai o Saldo Teórico Total (que inclui o fundo de caixa)
    try:
        saldo_teorico_total = resumo['saldo_teorico'] 
    except KeyError:
        return jsonify({"message": "Erro na estrutura do relatório. Chave 'saldo_teorico' ausente."}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    # Registra o saldo TEÓRICO como o saldo contado
    rows_affected = fluxo_caixa_dao.fechar_caixa(id_fluxo_aberto, saldo_teorico_total)
    
    if rows_affected == 1:
        return jsonify({
            "message": f"Caixa {id_fluxo_aberto} fechado com sucesso.", 
            "auditoria_final": resumo
        }), HTTPStatus.OK
    else:
        return jsonify({"message": "Falha ao fechar caixa. O turno pode já estar fechado."}), HTTPStatus.BAD_REQUEST


@fluxo_caixa_bp.route('/<int:id_fluxo>', methods=['GET'])
def buscar_caixa_por_id(id_fluxo):
    """ Busca um registro de fluxo de caixa pelo ID. """
    fluxo_data = fluxo_caixa_dao.buscar_por_id(id_fluxo)
    
    if fluxo_data:
        return jsonify(fluxo_data), HTTPStatus.OK 
    else:
        return jsonify({"message": f"Registro de fluxo de caixa {id_fluxo} não encontrado."}), HTTPStatus.NOT_FOUND


@fluxo_caixa_bp.route('/relatorio/fechados', methods=['GET'])
def buscar_relatorio_caixas_fechados():
    """ Retorna todos os caixas fechados com movimentação e diferença calculadas. """
    
    relatorio = fluxo_caixa_service.obter_relatorio_caixas_fechados()
    
    if relatorio:
        return jsonify(relatorio), HTTPStatus.OK
    else:
        return jsonify({"message": "Nenhum caixa fechado encontrado para o relatório."}), HTTPStatus.NOT_FOUND


@fluxo_caixa_bp.route('/relatorio/<int:id_fluxo>', methods=['GET'])
def get_relatorio_fechamento(id_fluxo):
    """ Retorna o relatório de auditoria e saldo teórico de um caixa. """
    
    relatorio = fluxo_caixa_service.gerar_resumo_fechamento(id_fluxo)
    
    if relatorio is None:
        return jsonify({"message": f"Caixa ID {id_fluxo} não encontrado."}), HTTPStatus.NOT_FOUND
        
    return jsonify(relatorio), HTTPStatus.OK