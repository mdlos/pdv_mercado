# src/controllers/tipo_funcionario_controller.py

from flask import Blueprint, jsonify
from src.models.tipo_funcionario_dao import TipoFuncionarioDAO
from src.schemas.tipo_funcionario_schema import TipoFuncionarioSchema
from http import HTTPStatus

tipo_funcionario_bp = Blueprint('tipo_funcionario', __name__)
tipo_funcionario_dao = TipoFuncionarioDAO()
tipos_funcionario_schema = TipoFuncionarioSchema(many=True)

@tipo_funcionario_bp.route('/', methods=['GET'])
def get_all_tipos():
    """ Rota para listar todos os cargos/tipos de funcionário. """
    data = tipo_funcionario_dao.find_all()
    
    if data is not None:
        result = tipos_funcionario_schema.dump(data)
        return jsonify(result), HTTPStatus.OK
    else:
        return jsonify({"message": "Erro ao buscar tipos de funcionário."}), HTTPStatus.INTERNAL_SERVER_ERROR