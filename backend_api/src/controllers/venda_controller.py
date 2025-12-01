# src/controllers/venda_controller.py

from flask import Blueprint, request, jsonify
import logging
from src.schemas.venda_schema import VendaSchema
from src.models.venda_dao import VendaDAO
from marshmallow import ValidationError
from http import HTTPStatus
from datetime import date 
from src.utils.formatters import clean_only_numbers # Import CORRIGIDO

# Instanciação dos objetos globais (necessário para todas as rotas)
venda_dao = VendaDAO() 
venda_schema = VendaSchema() 

venda_bp = Blueprint('venda', __name__, url_prefix='/api/v1/vendas')
logger = logging.getLogger(__name__)


@venda_bp.route('/', methods=['POST'])
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
        # AQUI o código está mais complexo, pois tem o cálculo de troco/total
        
        # 🚨 NOTA: Se você não implementou a lógica de retorno do Troco no Controller,
        # o DAO registra o valor total, mas o Controller precisa buscar o objeto completo.
        
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
# R - READ (Busca por ID / Número da Nota)
# -----------------------------------------------------------
@venda_bp.route('/<int:id_venda>', methods=['GET'])
def get_venda_by_id(id_venda):
    """ Rota para buscar uma venda e seus detalhes (por número da nota). """
    
    venda_data = venda_dao.buscar_por_id(id_venda)
    
    if venda_data:
        # Serializa o objeto completo com itens e pagamentos
        return venda_schema.dump(venda_data), HTTPStatus.OK
    else:
        return jsonify({"message": f"Venda com ID {id_venda} não encontrada."}), HTTPStatus.NOT_FOUND

# -----------------------------------------------------------
# R - READ ALL / BUSCA FLEXÍVEL (Todas as rotas de consulta em um só lugar)
# -----------------------------------------------------------
@venda_bp.route('/', methods=['GET'])
@venda_bp.route('/hoje', methods=['GET'])
@venda_bp.route('/busca', methods=['GET'])
def get_vendas_flexivel():
    """ 
    Rota unificada para todas as buscas GET:
    Lógica: Prioridade: ID Venda > CPF Cliente > Data > Listar Todos.
    """
    
    # 1. Captura e Limpa os parâmetros da URL
    data_str = request.args.get('data')
    cpf_cliente = request.args.get('cpf')
    id_venda_str = request.args.get('id_venda') 

    # Trata a rota /hoje
    if request.path.endswith('/hoje'):
        data_str = date.today().isoformat()
        
    # Variáveis para armazenar o filtro exclusivo a ser enviado para o DAO
    filter_data = None
    filter_cpf = None
    filter_id = None
    
    # 2. Determina o filtro principal (Lógica OU Exclusivo)
    
    # Prioridade 1: ID da Venda (Número da Nota)
    if id_venda_str:
        try:
            id_venda = int(id_venda_str)
            # Chama o método que busca a venda completa
            return get_venda_by_id(id_venda) 
        except ValueError:
            return jsonify({"message": "O parâmetro 'id_venda' deve ser um número inteiro."}), HTTPStatus.BAD_REQUEST
    
    # Prioridade 2: CPF do Cliente
    elif cpf_cliente:
        filter_cpf = clean_only_numbers(cpf_cliente)
        
    # Prioridade 3: Data (Inclui a busca /hoje)
    elif data_str:
        filter_data = data_str
        
    # 4. Executa a busca (Com 1 filtro ativo ou nenhum, para "Listar Todos")
    vendas_data = venda_dao.buscar_vendas_flexivel(
        data_str=filter_data, 
        cpf_cliente=filter_cpf
    )

    # 5. Serialização e Resposta
    if vendas_data:
        return venda_schema.dump(vendas_data, many=True), HTTPStatus.OK
    
    # Resposta 404
    if filter_data or filter_cpf or id_venda_str:
        return jsonify({"message": "Nenhuma venda encontrada com os filtros fornecidos."}), HTTPStatus.NOT_FOUND
    else:
        # Resposta para GET / (Listar Todos) quando não há vendas
        return jsonify({"message": "Nenhuma venda registrada no sistema."}), HTTPStatus.NOT_FOUND