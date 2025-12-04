# src/schemas/produto_schema.py

from marshmallow import Schema, fields, validate

class ProdutoSchema(Schema):
    codigo_produto = fields.Int(dump_only=True)
    
    # ------------------------------------
    # CAMPO DE SAÍDA NECESSÁRIO (Adicionado)
    # ------------------------------------
    quantidade = fields.Int(dump_only=True) 
    
    # Código de Barras (Opcional)
    codigo_barras = fields.Str(
        required=False,
        validate=validate.Length(max=50),
        allow_none=True
    )
    
    # Campo 'unidade_medida' REMOVIDO
    
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
    
    # Quantidade Inicial (Apenas para ENTRADA / CREATE)
    initial_quantity = fields.Int(
        required=False,
        load_only=True, # IMPORTANTE: Só aceita na criação/POST
        validate=validate.Range(min=0),
        load_default=0 
    )