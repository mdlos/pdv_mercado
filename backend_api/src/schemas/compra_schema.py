# src/schemas/compra_schema.py (FINAL E CORRIGIDO)

from marshmallow import Schema, fields, validate, post_load, ValidationError
from decimal import Decimal
from datetime import date
from src.utils.formatters import clean_only_numbers 

# --- Schemas Aninhados ---

class CompraItemSchema(Schema):
    """ Validação dos dados de cada item (produto) da compra. """
    codigo_produto = fields.Int(required=True, validate=validate.Range(min=1))
    quantidade_comprada = fields.Int(required=True, validate=validate.Range(min=1))
    
    # 🛑 Usamos o nome da coluna no DB
    custo_unitario = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal('0.01')))
    
    subtotal = fields.Decimal(dump_only=True, as_string=True)
    
    @post_load
    def calculate_subtotal(self, data, **kwargs):
        """ Calcula o subtotal do item. """
        data['subtotal'] = data['quantidade_comprada'] * data['custo_unitario']
        return data


# --- Schema Principal da Compra ---

class CompraSchema(Schema):
    """ Validação e agregação de uma compra completa. """
    
    # Chaves Estrangeiras (Obrigatório)
    id_fornecedor = fields.Int(required=True, validate=validate.Range(min=1))
    cpf_funcionario = fields.Str(required=True, validate=validate.Length(equal=11)) 
    
    # Detalhes da Compra
    id_compra = fields.Int(dump_only=True) 
    data_compra = fields.Date(required=False, load_default=date.today().isoformat()) 
    
    # 🛑 CORREÇÃO CRÍTICA AQUI: O valor total é CALCULADO, logo é DUMP_ONLY.
    valor_total_compra = fields.Decimal(dump_only=True, as_string=True)
    
    # Lista Aninhada
    itens = fields.List(fields.Nested(CompraItemSchema), required=True, validate=validate.Length(min=1))
    
    # -------------------------------------------------------------
    # Validação de Negócio
    # -------------------------------------------------------------

    @post_load
    def clean_and_validate_compra(self, data, **kwargs):
        """ 
        1. Calcula o valor total real da compra (soma dos subtotais dos itens).
        2. ATRIBUI o valor calculado ao campo 'valor_total_compra'.
        """
        # 1. Cálculo do Valor Total Real
        valor_calculado = Decimal(0)
        for item in data['itens']:
            valor_calculado += item['subtotal']
        
        # 🛑 NOVO FLUXO: Atribui o valor calculado à variável que será usada no DAO
        data['valor_total_compra'] = valor_calculado 
        
        return data