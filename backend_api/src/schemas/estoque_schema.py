# src/schemas/estoque_schema.py

from marshmallow import Schema, fields, validate

class EstoqueSchema(Schema):
    # O código do produto é a FK/PK
    codigo_produto = fields.Int(required=True)
    
    # A quantidade deve ser um inteiro não negativo
    quantidade = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )