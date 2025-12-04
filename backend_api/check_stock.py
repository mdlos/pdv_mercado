
from src.db_connection import get_db_connection
from psycopg import rows

def check_stock():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to DB")
        return

    try:
        with conn.cursor(row_factory=rows.dict_row) as cur:
            # Join estoque with produto to get names
            sql = """
                SELECT e.codigo_produto, p.nome, e.quantidade 
                FROM estoque e
                JOIN produto p ON e.codigo_produto = p.codigo_produto
                ORDER BY e.codigo_produto
            """
            cur.execute(sql)
            rows_data = cur.fetchall()
            print(f"Estoque atual:")
            for row in rows_data:
                print(f"ID: {row['codigo_produto']} | Produto: {row['nome']} | Qtd: {row['quantidade']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_stock()
