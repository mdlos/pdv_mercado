# src/schemas/fluxo_caixa_schema.py (FINAL E COMPLETO)

from marshmallow import Schema, fields, validate, post_load
from decimal import Decimal
from src.utils.formatters import clean_only_numbers 

class FluxoCaixaSchema(Schema):
    """ Validação dos dados para abertura e fechamento de caixa. """
    
    # --- CAMPOS DUMP_ONLY (SAÍDA DO DB) ---
    id_fluxo = fields.Int(dump_only=True)
    data_abertura = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    data_fechamento = fields.DateTime(dump_only=True)
    
    # 🛑 CAMPO ESSENCIAL DE SAÍDA: O valor inicial do caixa (do DB)
    saldo_inicial = fields.Decimal(dump_only=True, as_string=True)
    
    # 🛑 CAMPO ESSENCIAL DE SAÍDA: O valor final informado (do DB)
    saldo_final_informado = fields.Decimal(dump_only=True, as_string=True)

    # --- CAMPOS DE CARGA (INPUT/LOAD) ---
    
    # 1. Entrada para ABRIR o caixa (Recebe o CPF do funcionário)
    cpf_funcionario = fields.Str(required=False, validate=validate.Length(equal=11))
    
    # 2. Entrada para ABRIR o caixa (Recebe o valor inicial)
    valor_inicial = fields.Decimal(required=False, as_string=True, validate=validate.Range(min=Decimal('0.00')))
    
    # 3. Entrada para FECHAR o caixa (Recebe o saldo final informado)
    saldo_final_informado_input = fields.Decimal(required=False, as_string=True) # Nome alternativo para INPUT

    @post_load
    def clean_cpf(self, data, **kwargs):
        """ Limpa o CPF na carga. """
        # Garante que o CPF é limpo (apenas números) antes de passar para o DAO
        if data.get('cpf_funcionario'):
            data['cpf_funcionario'] = clean_only_numbers(data['cpf_funcionario'])
        return data