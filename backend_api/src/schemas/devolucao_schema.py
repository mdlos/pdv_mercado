# src/schemas/devolucao_schema.py (FINAL E CORRIGIDO)

from marshmallow import Schema, fields, validate, post_load
from decimal import Decimal
from src.utils.formatters import clean_only_numbers 

# --- Schemas Aninhados ---

class DevolucaoItemSchema(Schema):
    """ Validação dos dados de cada item (produto) devolvido. """
    codigo_produto = fields.Int(required=True, validate=validate.Range(min=1))
    quantidade_devolvida = fields.Int(required=True, validate=validate.Range(min=1))
    valor_unitario = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal('0.01')))


# --- Schema Principal da Devolução ---

class DevolucaoSchema(Schema):
    """ Validação e agregação de uma devolução completa. """
    
    # -------------------------------------------------------------
    # CHAVES ESTRANGEIRAS E IDENTIFICAÇÃO
    # -------------------------------------------------------------
    
    id_devolucao = fields.Int(dump_only=True)
    id_venda = fields.Int(required=True, validate=validate.Range(min=1))
    
    # 🛑 CPF do Cliente é obrigatório para vincular o Vale Crédito
    cpf_cliente = fields.Str(required=True, validate=validate.Length(equal=11))
    
    # 🛑 NOVO: CPF do Funcionário que fez o registro (Obrigatório para Auditoria)
    cpf_funcionario = fields.Str(required=True, validate=validate.Length(equal=11)) 
    
    # Detalhes da Devolução
    motivo = fields.Str(required=False, allow_none=True)
    
    # Lista Aninhada
    itens = fields.List(fields.Nested(DevolucaoItemSchema), required=True, validate=validate.Length(min=1))
    
    # -------------------------------------------------------------
    # Validação de Negócio e Limpeza
    # -------------------------------------------------------------

    @post_load
    def clean_and_calculate_return(self, data, **kwargs):
        """ 
        Limpa CPFs e calcula o valor total do crédito. 
        """
        # 1. Limpa o CPF do Cliente
        data['cpf_cliente'] = clean_only_numbers(data['cpf_cliente'])
        
        # 🛑 NOVO: Limpa o CPF do Funcionário
        data['cpf_funcionario'] = clean_only_numbers(data['cpf_funcionario'])
        
        # 2. Calcula o Total do Crédito
        valor_total_devolucao = Decimal(0)
        for item in data['itens']:
            valor_total_devolucao += item['quantidade_devolvida'] * item['valor_unitario']
            
        # Adiciona o valor total calculado ao dicionário de dados
        data['valor_total_devolucao'] = valor_total_devolucao
        
        return data