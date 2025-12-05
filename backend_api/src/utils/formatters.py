# src/utils/formatters.py 

import re

def clean_only_numbers(value):
    """ Remove todos os caracteres que não são dígitos. """
    if value is None:
        return None
    return re.sub(r'\D', '', str(value))

def format_telefone(value):
    """ Formata um número de telefone com 10 ou 11 dígitos para (DD) 9XXXX-XXXX. """
    if not value: return value
    
    # Limpa: Deixa apenas números
    numeros = clean_only_numbers(value)
    
    # Verifica o tamanho (10 ou 11 dígitos)
    tamanho = len(numeros)
    
    if tamanho == 11: # Celular com 9º dígito (XX) 9XXXX-XXXX
        return f"({numeros[0:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif tamanho == 10: # Fixo ou celular antigo (XX) XXXX-XXXX
        return f"({numeros[0:2]}) {numeros[2:6]}-{numeros[6:]}"
    else:
        return value # Retorna o valor original se o formato for desconhecido

def format_cpf_cnpj(value):
    """ Formata um CPF (11 dígitos) ou CNPJ (14 dígitos). """
    if not value: return value
    
    numeros = clean_only_numbers(value)
    tamanho = len(numeros)
    
    if tamanho == 11: # CPF: XXX.XXX.XXX-XX
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    elif tamanho == 14: # CNPJ: XX.XXX.XXX/XXXX-XX
        return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
    else:
        return value

def get_doc_type(value):
    """ Retorna 'cpf' ou 'cnpj' com base no número de dígitos. """
    if not value: return None
    
    numeros = clean_only_numbers(value)
    tamanho = len(numeros)
    
    if tamanho == 11:
        return 'cpf'
    elif tamanho == 14:
        return 'cnpj'
    else:
        return 'invalido'