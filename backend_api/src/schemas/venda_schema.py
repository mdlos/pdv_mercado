# src/schemas/venda_schema.py

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from src.utils.formatters import clean_only_numbers
from decimal import Decimal

# --- Schemas Aninhados ---

class PagamentoSchema(Schema):
    """ Validação dos dados de cada forma de pagamento. """
    id_tipo = fields.Int(required=True, validate=validate.Range(min=1)) # ID do tipo de pagamento (Ex: 1-Dinheiro, 2-Cartão)
    valor_pago = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal('0.01'))) # Valor total pago
    
    @post_load
    def clean_data_on_load(self, data, **kwargs):
        """ Garante que o valor_pago é tratado como Decimal. """
        # O fields.Decimal já faz isso, mas podemos garantir o tipo aqui se necessário
        return data


class VendaItemSchema(Schema):
    """ Validação dos dados de cada item (produto) da venda. """
    codigo_produto = fields.Int(required=True, validate=validate.Range(min=1))
    quantidade_venda = fields.Int(required=True, validate=validate.Range(min=1))
    # Note: O preço unitário que vem na requisição é o preço na hora da venda.
    preco_unitario = fields.Decimal(required=True, as_string=True, validate=validate.Range(min=Decimal('0.01')))
    
    @post_load
    def calculate_subtotal(self, data, **kwargs):
        """ Calcula o subtotal do item. """
        data['subtotal'] = data['quantidade_venda'] * data['preco_unitario']
        return data


# --- Schema Principal da Venda ---

class VendaSchema(Schema):
    """ Validação e agregação de uma venda completa. """
    # Chaves Estrangeiras (Entidades)
    cpf_funcionario = fields.Str(required=True, validate=validate.Length(equal=11))
    cpf_cliente = fields.Str(required=False, allow_none=True, validate=validate.Length(equal=11))
    
    # Detalhes da Venda
    valor_total = fields.Decimal(dump_only=True, as_string=True)
    
    # Listas Aninhadas
    itens = fields.List(fields.Nested(VendaItemSchema), required=True, validate=validate.Length(min=1))
    pagamentos = fields.List(fields.Nested(PagamentoSchema), required=True, validate=validate.Length(min=1))

    # --- Pre-processamento e Validação de Negócio ---

    @post_load
    def clean_and_validate_sale(self, data, **kwargs):
        """ 
        1. Limpa CPFs. 
        2. Calcula o valor total da venda.
        3. Valida se o valor pago é igual ao valor total da venda.
        """
        # 1. Limpeza
        data['cpf_funcionario'] = clean_only_numbers(data['cpf_funcionario'])
        if data.get('cpf_cliente'):
            data['cpf_cliente'] = clean_only_numbers(data['cpf_cliente'])
            
        # 2. Cálculo do Valor Total da Venda (soma dos subtotais dos itens)
        valor_total_venda = Decimal(0)
        for item in data['itens']:
            valor_total_venda += item['subtotal']
        data['valor_total'] = valor_total_venda
        
        # 3. Cálculo do Total Pago (soma dos valores dos pagamentos)
        total_pago = Decimal(0)
        for pagamento in data['pagamentos']:
            total_pago += pagamento['valor_pago']
        
        # 4. VALIDAÇÃO DE NEGÓCIO: O valor pago deve ser IGUAL ao valor da venda.
        if total_pago != valor_total_venda:
            raise ValidationError(
                f"O valor total pago ({total_pago:.2f}) não corresponde ao valor total da venda ({valor_total_venda:.2f})."
            )
        
        return data