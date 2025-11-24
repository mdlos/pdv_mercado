# src/schemas/devolucao_schema.py

from marshmallow import Schema, fields, validate, post_load
from decimal import Decimal

# --- Schemas Aninhados ---

class DevolucaoItemSchema(Schema):
    """ Validação dos dados de cada item (produto) devolvido. """
    codigo_produto = fields.Int(required=True, validate=validate.Range(min=1))
    quantidade_devolvida = fields.Int(required=True, validate=validate.Range(min=1))
    # NOTA: O preço unitário que deve ser usado para cálculo de crédito/reembolso será buscado do Venda_Item original
    valor_unitario = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal('0.01')))


# --- Schema Principal da Devolução ---

class DevolucaoSchema(Schema):
    """ Validação e agregação de uma devolução completa. """
    
    # Chaves Estrangeiras (Obrigatório)
    id_venda = fields.Int(required=True, validate=validate.Range(min=1))
    
    # Detalhes da Devolução
    motivo = fields.Str(required=False, allow_none=True)
    
    # Lista Aninhada
    itens = fields.List(fields.Nested(DevolucaoItemSchema), required=True, validate=validate.Length(min=1))
    
    # -------------------------------------------------------------
    # Validação de Negócio
    # -------------------------------------------------------------

    @post_load
    def calculate_total_return(self, data, **kwargs):
        """ Calcula o valor total da devolução (necessário para reembolso/crédito, se aplicável). """
        valor_total_devolucao = Decimal(0)
        for item in data['itens']:
            valor_total_devolucao += item['quantidade_devolvida'] * item['valor_unitario']
            
        data['valor_total_devolucao'] = valor_total_devolucao
        
        # NOTA: Aqui, a lógica de negócio mais complexa (como checar se a quantidade
        # devolvida não excede o que foi vendido originalmente) será feita no DAO.
        
        return data