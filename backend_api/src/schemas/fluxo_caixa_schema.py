# src/schemas/fluxo_caixa_schema.py

from marshmallow import Schema, fields, validate, post_load
from decimal import Decimal
from src.utils.formatters import clean_only_numbers

class FluxoCaixaSchema(Schema):
    # Identificador
    id_fluxo = fields.Int(dump_only=True)
    
    # Chave Estrangeira (Obrigatória na abertura)
    cpf_funcionario_abertura = fields.Str(required=True, validate=validate.Length(equal=11))
    
    # Dados de Abertura (Obrigatório no POST)
    saldo_inicial = fields.Decimal(
        required=True, 
        as_string=True,
        validate=validate.Range(min=Decimal('0.00'))
    )

    # Dados de Fechamento (Obrigatório no PUT)
    saldo_final_informado = fields.Decimal(
        required=False, 
        as_string=True,
        validate=validate.Range(min=Decimal('0.00'))
    )
    
    # Campos automáticos de status e data
    status = fields.Str(dump_only=True)
    data_hora_abertura = fields.DateTime(dump_only=True)
    @post_load
    def clean_data_on_load(self, data, **kwargs):
        """ Limpa o CPF do funcionário APENAS SE ESTIVER PRESENTE. """
        
        # CORREÇÃO: Adicionamos a verificação 'if' para evitar KeyError no PUT/PATCH
        if 'cpf_funcionario_abertura' in data:
            data['cpf_funcionario_abertura'] = clean_only_numbers(data['cpf_funcionario_abertura'])
            
        return data