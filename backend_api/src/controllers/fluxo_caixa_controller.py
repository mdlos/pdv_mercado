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
# O service agora será instanciado corretamente no arquivo services/fluxo_caixa_service.py
fluxo_caixa_service = FluxoCaixaService() 

# -----------------------------------------------------------
# POST - ABRIR CAIXA
# -----------------------------------------------------------
@fluxo_caixa_bp.route('/abrir', methods=['POST'])
def abrir_caixa():
    """ Rota para abrir o turno de caixa. """
    data = request.get_json()
    
    # 1. Validação
    try:
        validated_data = fluxo_caixa_schema.load(data) 
    except ValidationError as e:
        return jsonify({"message": "Erro de validação para abertura de caixa.", "errors": e.messages}), HTTPStatus.BAD_REQUEST
        
    cpf_funcionario = validated_data['cpf_funcionario']
    valor_inicial = validated_data['valor_inicial']
    
    # 2. VERIFICAÇÃO DE NEGÓCIO: Se já existe um caixa aberto
    if fluxo_caixa_dao.buscar_caixa_aberto(cpf_funcionario):
        return jsonify({"message": "Já existe um turno de caixa aberto para este funcionário."}), HTTPStatus.CONFLICT # 409
        
    # 3. CHAMADA AO DAO
    id_fluxo = fluxo_caixa_dao.abrir_caixa(cpf_funcionario, valor_inicial)
    if id_fluxo:
        return jsonify({
            "message": "Caixa aberto com sucesso.", 
            "id_fluxo": id_fluxo
        }), HTTPStatus.CREATED
    else:
        return jsonify({"message": "Falha ao abrir caixa. Verifique se o CPF é válido."}), HTTPStatus.INTERNAL_SERVER_ERROR

# -----------------------------------------------------------
# PUT - FECHAR CAIXA
# -----------------------------------------------------------
@fluxo_caixa_bp.route('/fechar/<string:cpf_funcionario>', methods=['PUT'])
def fechar_caixa(cpf_funcionario):
    """ 
    Rota para fechar o turno de caixa. O valor final é CALCULADO automaticamente.
    """
    
    # 1. VERIFICAÇÃO: Busca o ID do turno aberto
    id_fluxo_aberto = fluxo_caixa_dao.buscar_caixa_aberto(cpf_funcionario)
    
    if not id_fluxo_aberto:
        return jsonify({"message": "Nenhum turno de caixa aberto encontrado para este funcionário."}), HTTPStatus.NOT_FOUND
        
    # 2. 🛑 Ação CRÍTICA: GERA O SALDO TEÓRICO COMPLETO
    resumo = fluxo_caixa_service.gerar_resumo_fechamento(id_fluxo_aberto)

    # 🛑 CORREÇÃO AQUI: Verifica se o Service falhou em gerar o resumo
    if resumo is None:
        return jsonify({"message": "Falha ao gerar o resumo de auditoria. Verifique os dados do fluxo."}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    # 3. Extrai o Saldo Teórico Total (que inclui o fundo de caixa)
    # Esta linha só é executada se 'resumo' for um dicionário válido
    try:
        saldo_teorico_total = resumo['saldo_teorico'] 
    except KeyError:
        # Se a chave saldo_teorico estiver faltando no Service (erro de desenvolvimento/schema)
        return jsonify({"message": "Erro na estrutura do relatório. Chave 'saldo_teorico' ausente."}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    # 4. CHAMADA AO DAO: Registra o saldo TEÓRICO como o saldo contado (Auto-Fechamento)
    rows_affected = fluxo_caixa_dao.fechar_caixa(id_fluxo_aberto, saldo_teorico_total)
    
    if rows_affected == 1:
        # 5. Retorna o Relatório Analítico completo
        return jsonify({
            "message": f"Caixa {id_fluxo_aberto} fechado com sucesso.", 
            "auditoria_final": resumo
        }), HTTPStatus.OK
    else:
        return jsonify({"message": "Falha ao fechar caixa. O turno pode já estar fechado."}), HTTPStatus.INTERNAL_SERVER_ERROR
# -----------------------------------------------------------
# GET - BUSCAR CAIXA ABERTO / POR ID
# -----------------------------------------------------------
@fluxo_caixa_bp.route('/<int:id_fluxo>', methods=['GET'])
def buscar_caixa_por_id(id_fluxo):
    """ Busca um registro de fluxo de caixa pelo ID. """
    fluxo_data = fluxo_caixa_dao.buscar_por_id(id_fluxo)
    
    if fluxo_data:
        # Retorna o JSON do registro (sem serialização complexa, o foco é a funcionalidade)
        return jsonify(fluxo_data), HTTPStatus.OK 
    else:
        return jsonify({"message": f"Registro de fluxo de caixa {id_fluxo} não encontrado."}), HTTPStatus.NOT_FOUND

# -----------------------------------------------------------
# GET - RELATÓRIO DE CAIXAS FECHADOS (Auditoria de Todos)
# -----------------------------------------------------------
@fluxo_caixa_bp.route('/relatorio/fechados', methods=['GET'])
def buscar_relatorio_caixas_fechados():
    """ Retorna todos os caixas fechados com movimentação e diferença calculadas. """
    
    relatorio = fluxo_caixa_service.obter_relatorio_caixas_fechados()
    
    if relatorio:
        # Retorna o relatório formatado pelo Service
        return jsonify(relatorio), HTTPStatus.OK
    else:
        return jsonify({"message": "Nenhum caixa fechado encontrado para o relatório."}), HTTPStatus.NOT_FOUND
        
# -----------------------------------------------------------
# GET - RELATÓRIO INDIVIDUAL DE FECHAMENTO (Auditoria Pós-Fechamento)
# -----------------------------------------------------------
@fluxo_caixa_bp.route('/relatorio/<int:id_fluxo>', methods=['GET'])
def get_relatorio_fechamento(id_fluxo):
    """ Retorna o relatório de auditoria e saldo teórico de um caixa. """
    
    relatorio = fluxo_caixa_service.gerar_resumo_fechamento(id_fluxo)
    
    if relatorio is None:
        return jsonify({"message": f"Caixa ID {id_fluxo} não encontrado."}), HTTPStatus.NOT_FOUND
        
    return jsonify(relatorio), HTTPStatus.OK