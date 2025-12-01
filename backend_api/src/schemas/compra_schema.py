# src/schemas/compra_schema.py

from marshmallow import Schema, fields, validate, post_load
from decimal import Decimal
from datetime import date

# --- Schemas Aninhados ---

class CompraItemSchema(Schema):
    """ Validação dos dados de cada item (produto) da compra. """
    codigo_produto = fields.Int(required=True, validate=validate.Range(min=1))
    quantidade_compra = fields.Int(required=True, validate=validate.Range(min=1))
    # Preço unitário que você pagou pelo produto.
    preco_unitario = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal('0.01')))
    
    @post_load
    def calculate_subtotal(self, data, **kwargs):
        """ Calcula o subtotal do item. """
        # Garantir que o subtotal é calculado
        data['subtotal'] = data['quantidade_compra'] * data['preco_unitario']
        return data


# --- Schema Principal da Compra ---

class CompraSchema(Schema):
    """ Validação e agregação de uma compra completa. """
    
    # Chaves Estrangeiras (Obrigatório)
    id_fornecedor = fields.Int(required=True, validate=validate.Range(min=1))
    
    # Detalhes da Compra
    data_compra = fields.Date(required=False, load_default=date.today().isoformat()) 
    data_entrega = fields.Date(required=False, allow_none=True)
    valor_total_compra = fields.Decimal(dump_only=True, as_string=True)
    
    # Lista Aninhada
    itens = fields.List(fields.Nested(CompraItemSchema), required=True, validate=validate.Length(min=1))
    
    # -------------------------------------------------------------
    # Validação de Negócio
    # -------------------------------------------------------------

    @post_load
    def clean_and_validate_compra(self, data, **kwargs):
        """ 
        1. Calcula o valor total da compra.
        """
        # 1. Cálculo do Valor Total da Compra (soma dos subtotais dos itens)
        valor_total = Decimal(0)
        for item in data['itens']:
            valor_total += item['subtotal']
        data['valor_total_compra'] = valor_total
        
        return data