# src/schemas/cliente_schema.py

from marshmallow import Schema, fields, validate, post_load, post_dump, validates, ValidationError
from src.schemas.localizacao_schema import LocalizacaoSchema
from src.utils.formatters import clean_only_numbers, format_telefone, format_cpf_cnpj, get_doc_type
from marshmallow import validates, ValidationError

class ClienteSchema(Schema):
    # Campos que vêm diretamente do cliente
    id_cliente = fields.Int(dump_only=True)
    
    # Adicionamos id_localizacao para que o Marshmallow o veja e o possamos usar no get_localizacao_object
    id_localizacao = fields.Int(dump_only=True) 
    
    # CPF/CNPJ
    cpf_cnpj = fields.Str(
        required=True, 
        validate=validate.Length(min=11, max=14)
    )
    
    # TELEFONE
    telefone = fields.Str(
        required=False, 
        validate=validate.Length(min=10, max=15),
        allow_none=True,
    )

    nome = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=False, allow_none=True)
    sexo = fields.Str(required=False, validate=validate.OneOf(["M", "F", "O"]), allow_none=True)
    
    # --------------------------------------------------------------------------------------
    # LOCALIZACAO: Usamos fields.Method para forçar a estrutura aninhada na saída (GET),
    #              e fields.Nested para validar a entrada (POST/PUT).
    # --------------------------------------------------------------------------------------
    
    # 1. ENTRADA (POST/PUT): Usa o LocalizacaoSchema para validar o objeto aninhado
    localizacao = fields.Nested(LocalizacaoSchema, required=True, load_only=True) 

    # 2. SAÍDA (GET): Usa um método para montar o objeto aninhado a partir dos campos planos do DAO
    localizacao_saida = fields.Method("get_localizacao_object", dump_only=True)
    
    # --------------------------------------------------------------------------------------
    # MÉTODOS DE PROCESSAMENTO (Marshmallow)
    # --------------------------------------------------------------------------------------
    
    # Retorna o tipo de documento no JSON de saída
    tipo_doc = fields.Method("get_document_type", dump_only=True)

    @post_load
    def clean_fields_on_load(self, data, **kwargs):
        """ Limpa CPF/CNPJ e Telefone para salvar APENAS números no DB. """
        if 'cpf_cnpj' in data:
            data['cpf_cnpj'] = clean_only_numbers(data['cpf_cnpj'])
            
        if 'telefone' in data and data['telefone']:
            data['telefone'] = clean_only_numbers(data['telefone'])
            
        return data

    @post_dump
    def format_fields_on_dump(self, data, **kwargs):
        """ Formata Telefone e CPF/CNPJ para visualização (GET). """
        if 'telefone' in data and data['telefone']:
            data['telefone'] = format_telefone(data['telefone'])
            
        if 'cpf_cnpj' in data and data['cpf_cnpj']:
            data['cpf_cnpj'] = format_cpf_cnpj(data['cpf_cnpj'])
            
        return data
    
    # --- Métodos Auxiliares ---

    def get_document_type(self, obj):
        """ Retorna 'cpf' ou 'cnpj' com base no número de dígitos. """
        return get_doc_type(obj.get('cpf_cnpj'))
        
    def get_localizacao_object(self, obj):
        """ Monta o objeto aninhado 'localizacao' a partir do dicionário plano do DAO. """
        
        # Note que a formatação de CEP acontece no @post_dump, então pegamos o valor já formatado
        cep_formatado = obj.get('cep')
        
        return {
            "id_localizacao": obj.get('id_localizacao'),
            "cep": cep_formatado,
            "logradouro": obj.get('logradouro'),
            "numero": obj.get('numero'),
            "bairro": obj.get('bairro'),
            "cidade": obj.get('cidade'),
            "uf": obj.get('uf'),
        }
        @validates("cpf_cnpj")
        def validate_document_type(self, value): # Apenas 'self' e 'value' são necessários
            """ Verifica se o documento é um CPF (11) ou CNPJ (14) válido. """
            
            # Certifique-se de que a função clean_only_numbers está disponível (importada de formatters.py)
            from src.utils.formatters import clean_only_numbers
            
            cleaned_value = clean_only_numbers(value)
            if len(cleaned_value) not in [11, 14]:
                raise ValidationError("O CPF/CNPJ deve conter 11 (CPF) ou 14 (CNPJ) dígitos.")