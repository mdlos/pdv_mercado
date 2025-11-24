# src/controllers/fluxo_caixa_controller.py

from flask import Blueprint, request, jsonify
from src.schemas.fluxo_caixa_schema import FluxoCaixaSchema
from src.models.fluxo_caixa_dao import FluxoCaixaDAO
from marshmallow import ValidationError
from http import HTTPStatus
import logging
from decimal import Decimal
from src.services.fluxo_caixa_service import FluxoCaixaService # Import para a rota de relatório

logger = logging.getLogger(__name__)
fluxo_caixa_bp = Blueprint('fluxo_caixa', __name__, url_prefix='/api/v1/fluxo-caixa')

fluxo_caixa_dao = FluxoCaixaDAO()
fluxo_caixa_schema = FluxoCaixaSchema()
fluxo_caixa_service = FluxoCaixaService() # Instancia o service para relatórios

# -----------------------------------------------------------
# POST - ABRIR CAIXA
# -----------------------------------------------------------
@fluxo_caixa_bp.route('/', methods=['POST'])
def abrir_caixa():
    """ Rota para abrir o turno de caixa. """
    data = request.get_json()
    
    # 1. Validação
    try:
        # A validação básica do Marshmallow 3+ (partial=False/default) checa se campos required estão no JSON
        validated_data = fluxo_caixa_schema.load(data) 
        
        # ⚠️ Verificação de Presença: Garante que os campos required foram passados no JSON
        if 'cpf_funcionario_abertura' not in data or 'saldo_inicial' not in data:
            raise ValidationError({"message": "Campos obrigatórios (cpf_funcionario_abertura e saldo_inicial) ausentes no JSON."})

    except ValidationError as e:
        return jsonify({"message": "Erro de validação para abertura de caixa.", "errors": e.messages}), HTTPStatus.BAD_REQUEST
        
    cpf_funcionario = validated_data['cpf_funcionario_abertura']
    saldo_inicial = validated_data['saldo_inicial']
    
    # 2. VERIFICAÇÃO DE NEGÓCIO: Se já existe um caixa aberto
    if fluxo_caixa_dao.buscar_caixa_aberto(cpf_funcionario):
        return jsonify({"message": "Já existe um turno de caixa aberto para este funcionário."}), HTTPStatus.CONFLICT # 409
        
    # 3. CHAMADA AO DAO
    id_fluxo = fluxo_caixa_dao.abrir_caixa(cpf_funcionario, saldo_inicial)
    
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
    """ Rota para fechar o turno de caixa. """
    data = request.get_json()
    
    # 1. Validação 
    try:
        # Usamos partial=True porque o PUT só precisa do saldo final.
        validated_data = fluxo_caixa_schema.load(data, partial=True)
        
        if 'saldo_final_informado' not in validated_data:
             raise ValidationError({"saldo_final_informado": ["Campo obrigatório para fechamento de caixa ausente."]})

    except ValidationError as e:
        return jsonify({"message": "Erro de validação para fechamento de caixa.", "errors": e.messages}), HTTPStatus.BAD_REQUEST
        
    saldo_final_informado = validated_data['saldo_final_informado']
    
    # 2. VERIFICAÇÃO: Busca o ID do turno aberto
    id_fluxo_aberto = fluxo_caixa_dao.buscar_caixa_aberto(cpf_funcionario)
    
    if not id_fluxo_aberto:
        return jsonify({"message": "Nenhum turno de caixa aberto encontrado para este funcionário."}), HTTPStatus.NOT_FOUND # 404
        
    # 3. CHAMADA AO DAO
    rows_affected = fluxo_caixa_dao.fechar_caixa(id_fluxo_aberto, saldo_final_informado)
    
    if rows_affected == 1:
        return jsonify({"message": f"Caixa {id_fluxo_aberto} fechado com sucesso."}), HTTPStatus.OK
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
# GET - RELATÓRIO DE CAIXAS FECHADOS (Auditoria)
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