import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "v5_cantera_oro.db")

def align_db():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"=== ALIGNING DATABASE: {DB_PATH} ===\n")
    
    # 1. Create cantera_clientes if missing
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cantera_clientes';")
    exists = cursor.fetchone()
    
    if not exists:
        print("Table 'cantera_clientes' not found. Creating it.")
        cursor.execute('''CREATE TABLE cantera_clientes (
                            cuit TEXT PRIMARY KEY,
                            razon_social TEXT,
                            condicion_iva TEXT,
                            domicilio_fiscal TEXT,
                            sucursales_json TEXT
                        )''')
        print("[CREATED] Table 'cantera_clientes' created.")
    else:
        print("Table 'cantera_clientes' already exists.")

    conn.commit()
    conn.close()
    print("[SUCCESS] Database alignment complete.")

if __name__ == "__main__":
    align_db()
