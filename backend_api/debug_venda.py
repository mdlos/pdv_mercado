
import sys
import os
from decimal import Decimal

# Add src to path
sys.path.append(os.getcwd())

from src.models.venda_dao import VendaDAO
from src.schemas.venda_schema import VendaSchema

def debug():
    dao = VendaDAO()
    schema = VendaSchema()

    dados = {
        "cpf_funcionario": "00000000000",
        "itens": [
            {
                "codigo_produto": 1,
                "quantidade_venda": 1,
                "preco_unitario": "10.00"
            }
        ],
        "pagamentos": [
            {
                "id_tipo": 1,
                "valor_pago": "10.00"
            }
        ],
        "desconto": "0.00"
    }

    try:
        validated_data = schema.load(dados)
        print("Validation successful")
        print(validated_data)
        
        id_venda = dao.registrar_venda(validated_data)
        print(f"Sale registered with ID: {id_venda}")
    except Exception as e:
        print("Error occurred:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug()
