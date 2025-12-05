# src/schemas/tipo_funcionario_schema.py (FINAL E CORRIGIDO)

from marshmallow import Schema, fields, validate

class TipoFuncionarioSchema(Schema):
    """ Define o esquema para serialização do Tipo de Funcionário (Cargo). """
    
    id_tipo_funcionario = fields.Int(dump_only=True)
    
    cargo = fields.Str(required=True, validate=validate.Length(min=3, max=100))