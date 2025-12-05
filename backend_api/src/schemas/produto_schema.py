# src/schemas/produto_schema.py

from marshmallow import Schema, fields, validate

class ProdutoSchema(Schema):
    codigo_produto = fields.Int(dump_only=True)
    
    quantidade = fields.Int(dump_only=True) 
    
    codigo_barras = fields.Str(
        required=False,
        validate=validate.Length(max=50),
        allow_none=True
    )
    
    nome = fields.Str(
        required=True, 
        validate=validate.Length(min=3, max=100)
    )
    
    descricao = fields.Str(
        required=True, 
        validate=validate.Length(min=5, max=500)
    )
    
    preco = fields.Decimal(
        required=True,
        as_string=True,
        places=2,
        validate=validate.Range(min=0.01)
    )
    
    initial_quantity = fields.Int(
        required=False,
        load_only=True, 
        validate=validate.Range(min=0),
        load_default=0 
    )