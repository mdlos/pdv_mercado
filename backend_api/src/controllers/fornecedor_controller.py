# src/controllers/fornecedor_controller.py 

from flask import Blueprint, request, jsonify
from src.schemas.fornecedor_schema import FornecedorSchema
from src.models.fornecedor_dao import FornecedorDAO
from src.utils.formatters import clean_only_numbers
from http import HTTPStatus
import logging

logger = logging.getLogger(__name__)

fornecedor_bp = Blueprint('fornecedor', __name__)
fornecedor_dao = FornecedorDAO()
fornecedor_schema = FornecedorSchema()
fornecedores_schema = FornecedorSchema(many=True) 


@fornecedor_bp.route('/', methods=['POST'])
def create_fornecedor():
    """ Rota para criar um novo fornecedor. """
    data = request.get_json()
    
    # Validação dos dados
    try:
        valid_data = fornecedor_schema.load(data)
    except Exception as e:
        error_details = getattr(e, 'messages', str(e))
        return jsonify({"message": "Erro de validação", "errors": error_details}), HTTPStatus.BAD_REQUEST

    # Processa e Limpa os dados
    cnpj_limpo = clean_only_numbers(valid_data['cnpj'])
    localizacao_data = valid_data.pop('localizacao', None)
    
    # Inserção no Banco de Dados
    try:
        id_inserido = fornecedor_dao.insert(
            cnpj=cnpj_limpo,
            razao_social=valid_data['razao_social'],
            email=valid_data['email'],
            celular=valid_data.get('celular'),
            situacao_cadastral=valid_data.get('situacao_cadastral'),
            data_abertura=valid_data.get('data_abertura'),
            localizacao_data=localizacao_data
        )
        
        if id_inserido:
            novo_fornecedor_data = fornecedor_dao.find_by_id(id_inserido)
            return fornecedor_schema.dump(novo_fornecedor_data), HTTPStatus.CREATED
        else:
            return jsonify({"message": "Não foi possível inserir o fornecedor (pode ser CNPJ ou Email duplicado)."}), HTTPStatus.INTERNAL_SERVER_ERROR

    except Exception as e:
        logger.error(f"Erro inesperado ao criar fornecedor: {e}")
        return jsonify({"message": f"Erro interno no servidor: {e}"}), HTTPStatus.INTERNAL_SERVER_ERROR


@fornecedor_bp.route('/', methods=['GET'])
def get_all_fornecedores():
    """ Rota para listar todos os fornecedores. """
    fornecedores_data = fornecedor_dao.find_all()
    if fornecedores_data is not None:
        return fornecedores_schema.dump(fornecedores_data), HTTPStatus.OK
    return jsonify({"message": "Erro ao buscar fornecedores."}), HTTPStatus.INTERNAL_SERVER_ERROR

@fornecedor_bp.route('/<int:id_fornecedor>', methods=['GET'])
def get_fornecedor(id_fornecedor):
    """ Rota para buscar um fornecedor pelo ID. """
    
    fornecedor_data = fornecedor_dao.find_by_id(id_fornecedor)
    
    if fornecedor_data:
        return fornecedor_schema.dump(fornecedor_data), HTTPStatus.OK
    else:
        return jsonify({"message": f"Fornecedor com ID {id_fornecedor} não encontrado."}), HTTPStatus.NOT_FOUND


@fornecedor_bp.route('/<int:id_fornecedor>', methods=['PUT'])
def update_fornecedor(id_fornecedor):
    """ Rota para atualizar dados do fornecedor. """
    data = request.get_json()
    
    try:
        valid_data = fornecedor_schema.load(data, partial=True)
    except Exception as e:
        error_details = getattr(e, 'messages', str(e))
        return jsonify({"message": "Erro de validação", "errors": error_details}), HTTPStatus.BAD_REQUEST

    if not valid_data:
        return jsonify({"message": "Nenhum dado válido fornecido para atualização."}), HTTPStatus.BAD_REQUEST

    localizacao_data = valid_data.pop('localizacao', None)
    
    # 3. Limpeza de CNPJ/Celular (se fornecidos)
    if 'cnpj' in valid_data:
        valid_data['cnpj'] = clean_only_numbers(valid_data['cnpj'])
    if 'celular' in valid_data and valid_data['celular']:
        valid_data['celular'] = clean_only_numbers(valid_data['celular'])
        
    rows_affected = fornecedor_dao.update(
        id_fornecedor=id_fornecedor,
        localizacao_data=localizacao_data,
        **valid_data 
    )

    if rows_affected == 1:
        return jsonify({"message": f"Fornecedor {id_fornecedor} atualizado com sucesso."}), HTTPStatus.OK
    elif rows_affected == 0:
        return jsonify({"message": f"Fornecedor {id_fornecedor} encontrado, mas nenhum dado foi alterado."}), HTTPStatus.OK
    else:
        return jsonify({"message": "Erro interno ao atualizar fornecedor.", "status": "Error"}), HTTPStatus.INTERNAL_SERVER_ERROR

@fornecedor_bp.route('/<int:id_fornecedor>', methods=['DELETE'])
def delete_fornecedor(id_fornecedor):
    """ Rota para deletar um fornecedor e sua localização associada. """
    
    rows_affected = fornecedor_dao.delete(id_fornecedor)
    
    if rows_affected > 0:
        return '', HTTPStatus.NO_CONTENT 
    else:
        return jsonify({"message": f"Fornecedor com ID {id_fornecedor} não encontrado ou erro na exclusão."}), HTTPStatus.NOT_FOUND