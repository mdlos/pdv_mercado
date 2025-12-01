# src/schemas/venda_schema.py

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from src.utils.formatters import clean_only_numbers
from decimal import Decimal
from datetime import datetime 

# --- Schemas Aninhados ---

class PagamentoSchema(Schema):
    """ Validação dos dados de cada forma de pagamento. """
    id_pagamento = fields.Int(dump_only=True)
    id_tipo = fields.Int(required=True, validate=validate.Range(min=1)) 
    valor_pago = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal('0.01')))
    
    @post_load
    def clean_data_on_load(self, data, **kwargs):
        return data


class VendaItemSchema(Schema):
    """ Validação dos dados de cada item (produto) da venda. """
    id_venda = fields.Int(dump_only=True)
    codigo_produto = fields.Int(required=True, validate=validate.Range(min=1))
    
    quantidade_venda = fields.Int(required=True, validate=validate.Range(min=1))
    preco_unitario = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal('0.01')))
    
    @post_load
    def calculate_subtotal(self, data, **kwargs):
        """ Calcula o subtotal do item. """
        # Garantimos que o subtotal é calculado (essencial para o post_load da Venda)
        data['subtotal'] = data['quantidade_venda'] * data['preco_unitario']
        return data


# --- Schema Principal da Venda ---

class VendaSchema(Schema):
    """ Validação e agregação de uma venda completa. """
    
    # -----------------------------------------------------------------
    # CAMPOS DE SAÍDA NECESSÁRIOS
    # -----------------------------------------------------------------
    id_venda = fields.Int(dump_only=True)
    data_venda = fields.DateTime(dump_only=True) 
    valor_total = fields.Decimal(dump_only=True, as_string=True)
    
    # 🔑 CORREÇÃO CRÍTICA: TROCO deve ser um campo de saída (dump_only)
    troco = fields.Decimal(dump_only=True, as_string=True) 

    # Chaves Estrangeiras (Entidades)
    cpf_funcionario = fields.Str(required=True, validate=validate.Length(equal=11))
    cpf_cliente = fields.Str(required=False, allow_none=True, validate=validate.Length(equal=11))
    
    # Listas Aninhadas (Configuradas para aceitar INPUT e retornar OUTPUT)
    itens = fields.List(fields.Nested(VendaItemSchema), required=True, validate=validate.Length(min=1))
    pagamentos = fields.List(fields.Nested(PagamentoSchema), required=True, validate=validate.Length(min=1))

    # --- Pre-processamento e Validação de Negócio (LÓGICA DE TROCO) ---

    @post_load
    def clean_and_validate_sale(self, data, **kwargs):
        """ 
        1. Limpa CPFs. 
        2. Calcula o valor total da venda.
        3. Valida se o valor pago é suficiente e calcula o troco.
        """
        # 1. Limpeza
        data['cpf_funcionario'] = clean_only_numbers(data['cpf_funcionario'])
        if data.get('cpf_cliente'):
            data['cpf_cliente'] = clean_only_numbers(data['cpf_cliente'])
            
        # 2. Cálculo do Valor Total da Venda
        valor_total_venda = Decimal(0)
        for item in data['itens']:
            valor_total_venda += item['subtotal']
        data['valor_total'] = valor_total_venda
        
        # 3. Cálculo do Total Pago
        total_pago = Decimal(0)
        is_cash_involved = False
        CASH_ID = 1 # Assumindo que 1 é o ID para Dinheiro
        
        for pagamento in data['pagamentos']:
            total_pago += pagamento['valor_pago']
            if pagamento['id_tipo'] == CASH_ID:
                is_cash_involved = True

        # 4. VALIDAÇÃO DE NEGÓCIO E CÁLCULO DE TROCO
        
        troco = Decimal(0)
        
        if total_pago < valor_total_venda:
            # Caso A: Pagamento insuficiente
            raise ValidationError(
                f"O valor total pago ({total_pago:.2f}) é insuficiente para a venda de ({valor_total_venda:.2f})."
            )
        
        if total_pago > valor_total_venda:
            # Caso B: Pagamento a mais (Troco necessário)
            if not is_cash_involved:
                # Se pagou a mais, mas não usou dinheiro, é erro
                raise ValidationError("Pagamentos eletrônicos (Cartão/PIX) devem ser no valor exato da venda.")
            
            # Cálculo do Troco
            troco = total_pago - valor_total_venda
        
        # O valor do troco é adicionado para serialização e uso em relatórios
        data['troco'] = troco
        
        return data