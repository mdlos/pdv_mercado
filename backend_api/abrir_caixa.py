
import sys
from src.models.fluxo_caixa_dao import FluxoCaixaDAO
from decimal import Decimal

def abrir_caixa(cpf):
    dao = FluxoCaixaDAO()
    # Check if already open
    id_aberto = dao.buscar_caixa_aberto(cpf)
    if id_aberto:
        print(f"Caixa já está aberto para o CPF {cpf} (ID: {id_aberto})")
        return

    # Open caixa with 0 initial balance
    id_novo = dao.abrir_caixa(cpf, Decimal('0.00'))
    if id_novo:
        print(f"Caixa aberto com sucesso para o CPF {cpf} (ID: {id_novo})")
    else:
        print(f"Falha ao abrir caixa para o CPF {cpf}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python abrir_caixa.py <CPF>")
    else:
        abrir_caixa(sys.argv[1])
