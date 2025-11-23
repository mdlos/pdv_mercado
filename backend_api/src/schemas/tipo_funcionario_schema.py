# src/schemas/tipo_funcionario_schema.py

from marshmallow import Schema, fields

class TipoFuncionarioSchema(Schema):
    id_tipo_funcionario = fields.Int(required=True)
    cargo = fields.Str(dump_only=True)