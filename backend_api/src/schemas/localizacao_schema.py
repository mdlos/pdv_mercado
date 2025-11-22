# src/schemas/localizacao_schema.py 

from marshmallow import Schema, fields, validate

class LocalizacaoSchema(Schema):
    """ Define a validação para os dados de endereço. """
    cep = fields.Str(required=True, validate=validate.Length(max=10))
    logradouro = fields.Str(required=False, validate=validate.Length(max=150), allow_none=True)
    numero = fields.Str(required=False, validate=validate.Length(max=10), allow_none=True)
    bairro = fields.Str(required=False, validate=validate.Length(max=100), allow_none=True)
    cidade = fields.Str(required=False, validate=validate.Length(max=100), allow_none=True)
    uf = fields.Str(required=False, validate=validate.Length(equal=2), allow_none=True)