
from src.db_connection import get_db_connection
from psycopg import rows

def list_open_caixas():
    conn = get_db_connection()
    if not conn:
        with open("caixa_output.txt", "w") as f:
            f.write("Failed to connect to DB")
        return

    try:
        with conn.cursor(row_factory=rows.dict_row) as cur:
            cur.execute("SELECT id_fluxo, cpf_funcionario_abertura, status FROM fluxo_caixa WHERE status = 'ABERTO'")
            rows_data = cur.fetchall()
            with open("caixa_output.txt", "w") as f:
                if not rows_data:
                    f.write("Nenhum caixa aberto encontrado.")
                else:
                    f.write(f"Encontrados {len(rows_data)} caixas abertos:\n")
                    for row in rows_data:
                        f.write(f"ID: {row['id_fluxo']}, CPF: {row['cpf_funcionario_abertura']}, Status: {row['status']}\n")
    except Exception as e:
        with open("caixa_output.txt", "w") as f:
            f.write(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_open_caixas()
