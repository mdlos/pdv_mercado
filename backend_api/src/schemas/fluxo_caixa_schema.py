# src/schemas/fluxo_caixa_schema.py (FINAL E COMPLETO)

from marshmallow import Schema, fields, validate, post_load
from decimal import Decimal
from src.utils.formatters import clean_only_numbers 

class FluxoCaixaSchema(Schema):
    """ Validação dos dados para abertura e fechamento de caixa. """
    
    id_fluxo = fields.Int(dump_only=True)
    data_abertura = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    data_fechamento = fields.DateTime(dump_only=True)
    
    # O valor inicial do caixa 
    saldo_inicial = fields.Decimal(dump_only=True, as_string=True)
    
    # O valor final informado 
    saldo_final_informado = fields.Decimal(dump_only=True, as_string=True)

    # CPF do Funcionário que fez o registro 
    cpf_funcionario = fields.Str(required=False, validate=validate.Length(equal=11))
    
    # Recebe o valor inicial
    valor_inicial = fields.Decimal(required=False, as_string=True, validate=validate.Range(min=Decimal('0.00')))
    
    # Recebe o saldo final informado
    saldo_final_informado_input = fields.Decimal(required=False, as_string=True) 

    @post_load
    def clean_cpf(self, data, **kwargs):
        """ Limpa o CPF na carga. """
        # Garante que o CPF é limpo (apenas números)
        if data.get('cpf_funcionario'):
            data['cpf_funcionario'] = clean_only_numbers(data['cpf_funcionario'])
        return data