# src/controllers/cliente_controller.py 

from flask import Blueprint, request, jsonify
from src.schemas.cliente_schema import ClienteSchema
from src.models.cliente_dao import ClienteDAO
from src.utils.formatters import clean_only_numbers
from http import HTTPStatus
import logging # Adicionar import para log

logger = logging.getLogger(__name__)

cliente_bp = Blueprint('clientes', __name__)
cliente_dao = ClienteDAO()
cliente_schema = ClienteSchema()
clientes_schema = ClienteSchema(many=True)

# -----------------------------------------------------------
# C - CREATE (Criação de Novo Cliente) - MANTIDO
# -----------------------------------------------------------
@cliente_bp.route('/', methods=['POST'], strict_slashes=False)
def create_cliente():
    """ Rota para criar um novo cliente. """
    data = request.get_json()
    
    try:
        validated_data = cliente_schema.load(data)
    except Exception as e:
        error_details = getattr(e, 'messages', str(e))
        return jsonify({"message": "Erro de validação", "errors": error_details}), HTTPStatus.BAD_REQUEST

    cpf_cnpj_limpo = clean_only_numbers(validated_data['cpf_cnpj'])
    telefone_limpo = clean_only_numbers(validated_data.get('telefone', ''))
    localizacao_data = validated_data.pop('localizacao', None)
    sexo = validated_data.get('sexo')
    sexo_final = sexo if sexo else None 

    try:
        id_inserido = cliente_dao.insert(
            cpf_cnpj=cpf_cnpj_limpo,
            nome=validated_data['nome'],
            email=validated_data.get('email'),
            telefone=telefone_limpo,
            sexo=sexo_final, 
            localizacao_data=localizacao_data
        )
        
        if id_inserido:
            novo_cliente_data = cliente_dao.find_by_id(id_inserido)
            return cliente_schema.dump(novo_cliente_data), HTTPStatus.CREATED
        else:
            return jsonify({"message": "Não foi possível inserir o cliente (CNPJ/CPF ou Email duplicado)."}), HTTPStatus.INTERNAL_SERVER_ERROR

    except Exception as e:
        logger.error(f"Erro interno ao criar cliente: {e}")
        return jsonify({"message": f"Erro interno ao criar cliente: {e}"}), HTTPStatus.INTERNAL_SERVER_ERROR

# -----------------------------------------------------------
# R - READ ALL (Busca Todos) - MANTIDO
# -----------------------------------------------------------
@cliente_bp.route('/', methods=['GET'], strict_slashes=False)
def get_all_clientes():
    """ Rota para buscar todos os clientes cadastrados. """
    
    clientes_data = cliente_dao.find_all() 
    
    if clientes_data:
        return clientes_schema.dump(clientes_data, many=True), HTTPStatus.OK
    else:
        return jsonify([]), HTTPStatus.OK

# -----------------------------------------------------------
# R - READ ONE (Busca UNIFICADA por ID ou CPF/CNPJ) <--- ROTA CORRIGIDA
# -----------------------------------------------------------
@cliente_bp.route('/<string:identifier>', methods=['GET'])
def get_cliente_unificado(identifier):
    """ 
    Rota unificada: Tenta buscar por ID (se for INT) e, se falhar, busca por CPF/CNPJ (STRING).
    """
    cliente_data = None
    identifier_limpo = clean_only_numbers(identifier) # Limpa o identificador de qualquer forma

    # 1. TENTA BUSCAR POR ID (CHAVE PRIMÁRIA - INT)
    if identifier_limpo.isdigit():
        try:
            cliente_data = cliente_dao.find_by_id(int(identifier_limpo))
        except Exception as e:
            logger.warning(f"Busca por ID falhou: {e}")
            pass # Continua a busca por CPF/CNPJ
            
    # 2. TENTA BUSCAR POR CPF/CNPJ (CHAVE DE NEGÓCIO - STRING)
    if cliente_data is None:
        cliente_data = cliente_dao.find_by_cpf_cnpj(identifier_limpo)
    
    # 3. RETORNO FINAL
    if cliente_data:
        return cliente_schema.dump(cliente_data), HTTPStatus.OK
    else:
        return jsonify({"message": f"Cliente com ID ou CPF/CNPJ {identifier} não encontrado."}), HTTPStatus.NOT_FOUND

# -----------------------------------------------------------
# U - UPDATE (Atualização) - MANTIDO
# -----------------------------------------------------------
@cliente_bp.route('/<int:id_cliente>', methods=['PUT'])
def update_cliente(id_cliente):
    """ Rota para atualizar dados do cliente. """
    data = request.get_json()
    
    try:
        valid_data = cliente_schema.load(data, partial=True)
    except Exception as e:
        error_details = getattr(e, 'messages', str(e))
        return jsonify({"message": "Erro de validação", "errors": error_details}), HTTPStatus.BAD_REQUEST

    if not valid_data:
        return jsonify({"message": "Nenhum dado válido fornecido para atualização."}), HTTPStatus.BAD_REQUEST

    localizacao_data = valid_data.pop('localizacao', None)
    
    if 'cpf_cnpj' in valid_data:
        valid_data['cpf_cnpj'] = clean_only_numbers(valid_data['cpf_cnpj'])
    
    if 'telefone' in valid_data:
        valid_data['telefone'] = valid_data['telefone'] if valid_data['telefone'] else None
        if valid_data['telefone']:
            valid_data['telefone'] = clean_only_numbers(valid_data['telefone'])
    
    rows_affected = cliente_dao.update(
        id_cliente=id_cliente,
        localizacao_data=localizacao_data,
        **valid_data 
    )
    
    if rows_affected == 1:
        return jsonify({"message": f"Cliente {id_cliente} atualizado com sucesso."}), HTTPStatus.OK
    elif rows_affected == 0:
        return jsonify({"message": f"Cliente {id_cliente} encontrado, mas nenhum dado foi alterado."}), HTTPStatus.OK
    else:
        return jsonify({"message": "Erro interno ao atualizar cliente.", "status": "Error"}), HTTPStatus.INTERNAL_SERVER_ERROR

# -----------------------------------------------------------
# D - DELETE (Exclusão) - MANTIDO
# -----------------------------------------------------------
@cliente_bp.route('/<int:id_cliente>', methods=['DELETE'])
def delete_cliente(id_cliente):
    """ Rota para deletar um cliente e sua localização associada. """
    
    rows_affected = cliente_dao.delete(id_cliente)
    
    if rows_affected > 0:
        return '', HTTPStatus.NO_CONTENT 
    else:
        return jsonify({"message": f"Cliente com ID {id_cliente} não encontrado ou erro na exclusão."}), HTTPStatus.NOT_FOUND
