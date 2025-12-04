# src/schemas/venda_schema.py (FINAL COM CORREÇÃO DE INPUT/OUTPUT)

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from src.utils.formatters import clean_only_numbers, format_cpf_cnpj 
from decimal import Decimal
from datetime import datetime 

# --- Schemas Aninhados ---

class PagamentoSchema(Schema):
    """ Validação dos dados de cada forma de pagamento. """
    id_pagamento = fields.Int(dump_only=True)
    id_tipo = fields.Int(required=True, validate=validate.Range(min=1)) 
    
    # 🛑 CORREÇÃO UX: Tornar valor_pago opcional e permitir NULL na entrada
    valor_pago = fields.Decimal(
        required=False, 
        allow_none=True, 
        as_string=True, 
        validate=validate.Range(min=Decimal('0.00'))
    )
    
    descricao = fields.Str(dump_only=True) 
    troco = fields.Decimal(dump_only=True, as_string=True) 
    
    @post_load
    def clean_data_on_load(self, data, **kwargs):
        return data


class VendaItemSchema(Schema):
    """ Validação dos dados de cada item (produto) da venda. """
    id_venda = fields.Int(dump_only=True)
    
    nome_produto = fields.Str(dump_only=True) 

    codigo_produto = fields.Int(required=True, validate=validate.Range(min=1))
    
    quantidade_venda = fields.Int(required=True, validate=validate.Range(min=1))
    preco_unitario = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal('0.01')))
    
    subtotal = fields.Decimal(dump_only=True, as_string=True) 

    @post_load
    def calculate_subtotal(self, data, **kwargs):
        """ Calcula o subtotal do item. """
        data['subtotal'] = data['quantidade_venda'] * data['preco_unitario']
        return data


# --- Schema Principal da Venda ---

class VendaSchema(Schema):
    """ Validação e agregação de uma venda completa. """
    
    # 🛑 Define a lista de IDs de pagamento eletrônico/não-dinheiro
    CASH_ID = 1 
    NON_CASH_IDS = {2, 3, 4, 5, 6, 7}
    
    # -----------------------------------------------------------------
    # CAMPOS DE SAÍDA NECESSÁRIOS
    # -----------------------------------------------------------------
    id_venda = fields.Int(dump_only=True)
    data_venda = fields.DateTime(dump_only=True) 
    
    # Adicionar campos de Relacionamento (DUMP_ONLY)
    nome_caixa = fields.Str(dump_only=True)
    nome_cliente = fields.Str(dump_only=True) 
    
    # Adicionar campos da Configuração de Mercado (DUMP_ONLY)
    mercado_cnpj = fields.Str(dump_only=True)
    mercado_razao_social = fields.Str(dump_only=True)
    mercado_endereco = fields.Str(dump_only=True)
    mercado_contato = fields.Str(dump_only=True)
    
    valor_total = fields.Decimal(dump_only=True, as_string=True)
    troco = fields.Decimal(dump_only=True, as_string=True) 

    # Chaves Estrangeiras (Entidades)
    
    # 🛑 CORREÇÃO 1: CPF Funcionário (ENTRADA - INPUT)
    cpf_funcionario = fields.Str(required=True, validate=validate.Length(equal=11))
    
    # 🛑 CORREÇÃO 3: CPF Funcionário Formatado (SAÍDA - OUTPUT)
    cpf_funcionario_formatado = fields.Method(
        serialize='format_cpf_funcionario', 
        dump_only=True
    )
    
    # Coluna de entrada (input)
    cpf_cliente = fields.Str(required=False, allow_none=True, validate=validate.Length(equal=11))
    
    # Campo de Desconto (Input)
    desconto = fields.Decimal(load_default=0.0, allow_none=True, as_string=True)

    # 🛑 CORREÇÃO 2: CPF/CNPJ Cliente (Formatação na Saída)
    cpf_cnpj_cliente = fields.Method(
        serialize='format_cpf_cnpj_cliente', 
        dump_only=True, 
        allow_none=True
    )
    
    # Listas Aninhadas
    itens = fields.List(fields.Nested(VendaItemSchema), required=True, validate=validate.Length(min=1))
    pagamentos = fields.List(fields.Nested(PagamentoSchema), required=True, validate=validate.Length(min=1))

    # -----------------------------------------------------------------
    # MÉTODOS DE SERIALIZAÇÃO (Chamados durante o dump)
    # -----------------------------------------------------------------

    def format_cpf_funcionario(self, obj):
        """ Formata o CPF do funcionário (caixa) para exibição. """
        # O valor bruto é lido do campo 'cpf_funcionario' (que agora é fields.Str)
        return format_cpf_cnpj(obj['cpf_funcionario'])
    
    def format_cpf_cnpj_cliente(self, obj):
        """ Formata o CPF/CNPJ do cliente (se existir). """
        return format_cpf_cnpj(obj['cpf_cnpj_cliente'])

    # --- Pre-processamento e Validação de Negócio (LÓGICA DE TROCO) ---
    @post_load
    def clean_and_validate_sale(self, data, **kwargs):
        """ 
        1. Limpa CPFs. 
        2. Calcula o valor total da venda.
        3. Valida se o valor pago é suficiente e calcula o troco/auto-preenchimento.
        """
        # 1. Limpeza
        data['cpf_funcionario'] = clean_only_numbers(data['cpf_funcionario'])
        if data.get('cpf_cliente'):
            data['cpf_cliente'] = clean_only_numbers(data['cpf_cliente'])
            
        # 2. Cálculo do Valor Total da Venda
        valor_total_venda = Decimal(0)
        for item in data['itens']:
            valor_total_venda += item['subtotal']
        
        # Aplicar Desconto
        desconto = data.get('desconto')
        if desconto:
            valor_total_venda -= desconto
            
        data['valor_total'] = valor_total_venda
        
        # 3. Processamento de Pagamentos e Cálculo de Troco/Preenchimento
        total_pago = Decimal(0)
        is_cash_involved = False
        
        for pagamento in data['pagamentos']:
            pago_parcial = pagamento['valor_pago'] 
            
            # --- Regra de Inteligência (Auto-Preenchimento/Valor Exato) ---
            if pagamento['id_tipo'] == self.CASH_ID:
                is_cash_involved = True
            
            elif pagamento['id_tipo'] in self.NON_CASH_IDS:
                # 🛑 LÓGICA DE AUTO-PREENCHIMENTO: Se o valor pago for NULL/None, preenche com o total.
                if pago_parcial is None:
                    pagamento['valor_pago'] = valor_total_venda
                    pago_parcial = valor_total_venda 
                
                elif pago_parcial > valor_total_venda:
                    # 🛑 Falha na UX: Não se pode pagar a mais em Pix/Cartão
                    raise ValidationError("Pagamentos eletrônicos (Pix/Cartão) devem ser no valor exato da venda.", field_names=['valor_pago'])

            # 4. Acumular o total pago
            if pago_parcial is not None:
                 total_pago += pago_parcial

        # --- Validação Final e Troco ---
        troco = Decimal(0)
        
        if total_pago < valor_total_venda:
            raise ValidationError(
                f"O valor total pago ({total_pago:.2f}) é insuficiente para a venda de ({valor_total_venda:.2f})."
            )
        
        if total_pago > valor_total_venda:
            if not is_cash_involved:
                raise ValidationError("Pagamentos eletrônicos (Cartão/PIX) devem ser no valor exato da venda.")
            
            troco = total_pago - valor_total_venda
        
        data['troco'] = troco
        
        return data