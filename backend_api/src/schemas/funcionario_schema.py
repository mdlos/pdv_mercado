# src/schemas/funcionario_schema.py (FINAL COM REGRAS E FORMATAÇÃO)

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load, post_dump
from src.schemas.localizacao_schema import LocalizacaoSchema
# 🛑 Importações corrigidas
from src.utils.formatters import clean_only_numbers, format_telefone, format_cpf_cnpj 

class FuncionarioSchema(Schema):
    # Identificadores e Campos de Chave
    cpf = fields.Str(required=True, validate=validate.Length(equal=11))
    
    # 🛑 CORREÇÃO: O cargo é obrigatório na entrada para impor a regra de negócio
    id_tipo_funcionario = fields.Int(required=True, load_only=True) 
    
    # DADOS PESSOAIS
    nome = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    sobrenome = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=False, allow_none=True)
    sexo = fields.Str(required=False, validate=validate.OneOf(['M', 'F', 'O']), allow_none=True)
    telefone = fields.Str(required=False, allow_none=True)
    nome_social = fields.Str(required=False, allow_none=True)

    # SENHA: Apenas para entrada (LOAD_ONLY)
    # Valor que o gerente envia. Será hashed no Controller.
    senha = fields.Str(
        required=True, 
        load_only=True,
        validate=validate.Length(min=3, max=255)
    )
    senha_hashed = fields.Str(dump_only=True, data_key="senha")    # -------------------------------------------------------------
    # RELAÇÕES E ANINHAMENTO
    # -------------------------------------------------------------
    
    # 1. LOCALIZAÇÃO (INPUT): Aceita o dicionário de localização na entrada
    localizacao = fields.Nested(LocalizacaoSchema, required=False, allow_none=True, load_only=True)
    
    # 2. CARGO (OUTPUT): Retorna o objeto do cargo (GET)
    cargo = fields.Method("get_cargo_details", dump_only=True)
    
    # 3. LOCALIZAÇÃO (OUTPUT): Retorna o objeto de localização (GET)
    localizacao_detalhes = fields.Method("get_localizacao_object", dump_only=True)

    # 🛑 NOVO: Campo de saída formatado para o CPF do operador (que é a entrada)
    cpf_funcionario_formatado = fields.Method(
        serialize='format_cpf_funcionario', 
        dump_only=True
    )

    # -------------------------------------------------------------
    # MÉTODOS DE PROCESSAMENTO E FORMATAÇÃO
    # -------------------------------------------------------------
    
    @post_load
    def clean_data_on_load(self, data, **kwargs):
        """ Limpa CPF e Telefone para salvar APENAS números no DB. """
        if 'cpf' in data:
            data['cpf'] = clean_only_numbers(data['cpf'])
        if 'telefone' in data and data['telefone']:
            # 🛑 Chama a função de limpeza, não de formatação, para salvar no DB
            data['telefone'] = clean_only_numbers(data['telefone']) 
        
        return data

    @post_dump
    def format_fields_on_dump(self, data, **kwargs):
        """ Formata Telefone e CPF para visualização (GET). """
        if 'telefone' in data and data['telefone']:
            data['telefone'] = format_telefone(data['telefone'])
        if 'cpf' in data and data['cpf']:
            data['cpf'] = format_cpf_cnpj(data['cpf'])
            
        return data

    @validates("cpf")
    def validate_cpf_length(self, value, **kwargs): 
        """ Garante que o CPF, após a limpeza, tenha 11 dígitos. """
        if len(clean_only_numbers(value)) != 11:
            raise ValidationError("O CPF deve conter exatamente 11 dígitos.")

    # --- MÉTODOS AUXILIARES PARA SERIALIZAÇÃO DE SAÍDA ---
    
    def get_cargo_details(self, obj):
        """ Monta o objeto de cargo a partir dos dados planos (flat) do DAO. """
        if obj.get('id_tipo_funcionario'):
            return {
                "id": obj['id_tipo_funcionario'],
                "nome": obj.get('tipo_cargo', 'N/A') 
            }
        return None
        
    def get_localizacao_object(self, obj):
        """ Monta o objeto aninhado 'localizacao_detalhes' a partir do JOIN do DAO. """
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
        
    def format_cpf_funcionario(self, obj):
        """ Formata o CPF para o novo campo de saída. """
        return format_cpf_cnpj(obj['cpf'])