
from src.db_connection import get_db_connection

def add_column():
    conn = get_db_connection()
    if not conn: return

    try:
        with conn.cursor() as cur:
            cur.execute("ALTER TABLE venda ADD COLUMN IF NOT EXISTS desconto DECIMAL(10, 2) DEFAULT 0.00")
            conn.commit()
            print("Column 'desconto' added to 'venda' table.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
