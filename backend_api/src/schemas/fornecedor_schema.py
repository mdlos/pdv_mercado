# src/schemas/fornecedor_schema.py (VERSÃO FINAL E CORRIGIDA COM FORMATTERS)

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, post_dump
from src.schemas.localizacao_schema import LocalizacaoSchema
from src.utils.formatters import clean_only_numbers, format_cpf_cnpj, format_telefone # Import de formatters

class FornecedorSchema(Schema):
    # Identificadores e Chaves
    id_fornecedor = fields.Int(dump_only=True)
    cnpj = fields.Str(required=True, validate=validate.Length(equal=14)) 
    
    # Dados Pessoais
    razao_social = fields.Str(required=True, validate=validate.Length(min=5, max=150))
    situacao_cadastral = fields.Str(required=False, allow_none=True)
    data_abertura = fields.Date(required=False, allow_none=True)
    celular = fields.Str(required=False, allow_none=True)
    email = fields.Email(required=False, allow_none=True)

    # Relação: Localização
    localizacao = fields.Nested(LocalizacaoSchema, required=True, load_only=True)
    localizacao_detalhes = fields.Method("get_localizacao_object", dump_only=True)


    # MÉTODOS DE PROCESSAMENTO E VALIDAÇÃO    
    @post_load
    def clean_data_on_load(self, data, **kwargs):
        """ Limpa CNPJ e Celular para salvar APENAS números no DB. """
        if 'cnpj' in data:
            data['cnpj'] = clean_only_numbers(data['cnpj'])
        if 'celular' in data and data['celular']:
            data['celular'] = clean_only_numbers(data['celular'])
        
        return data

    @post_dump
    def format_fields_on_dump(self, data, **kwargs):
        """ 
        NOVO: Executado DEPOIS de carregar do banco (GET).
        Formata o CNPJ e o Celular para a visualização.
        """
        # Formata o CNPJ
        if 'cnpj' in data and data['cnpj']:
            data['cnpj'] = format_cpf_cnpj(data['cnpj'])
            
        # Formata o Celular/Telefone
        if 'celular' in data and data['celular']:
            data['celular'] = format_telefone(data['celular'])
            
        return data

    @validates("cnpj")
    def validate_cnpj_length(self, value, **kwargs):
        """ Garante que o CNPJ, após a limpeza, tenha 14 dígitos. """
        if len(clean_only_numbers(value)) != 14:
            raise ValidationError("O CNPJ deve conter exatamente 14 dígitos.")
    
    def get_localizacao_object(self, obj):
        """ Monta o objeto aninhado 'localizacao' a partir do JOIN do DAO. """
        # Verifica se os campos de localização existem
        if obj.get('id_localizacao'):
            return {
                "id_localizacao": obj['id_localizacao'],
                "cep": obj.get('cep'), 
                "logradouro": obj.get('logradouro'),
                "numero": obj.get('numero'),
                "bairro": obj.get('bairro'),
                "cidade": obj.get('cidade'),
                "uf": obj.get('uf'),
            }
        return None