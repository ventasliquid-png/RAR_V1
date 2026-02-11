import sqlite3
import shutil
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "v5_cantera_oro.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

def evolve_db():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] DB not found at {DB_PATH}")
        return

    # 1. Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BASE_DIR, "backups", f"{DB_NAME}.{timestamp}.bak")
    
    if not os.path.exists(os.path.join(BASE_DIR, "backups")):
        os.makedirs(os.path.join(BASE_DIR, "backups"))
        
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] Created at {backup_path}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 2. Add unidad_medida to cantera_productos
    print("--- Evolving cantera_productos ---")
    cursor.execute("PRAGMA table_info(cantera_productos)")
    cols = [c[1] for c in cursor.fetchall()]
    
    if "unidad_medida" not in cols:
        print("Adding column: unidad_medida")
        # Default to 'u' (unidades) or NULL
        cursor.execute("ALTER TABLE cantera_productos ADD COLUMN unidad_medida TEXT DEFAULT 'u'")
    else:
        print("Column unidad_medida already exists.")

    # 3. Handle Transacciones (remitos)
    print("--- Evolving Transacciones (remitos) ---")
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='remitos';")
    exists = cursor.fetchone()
    
    if not exists:
        print("Table 'remitos' not found. Creating it.")
        cursor.execute("""
            CREATE TABLE remitos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                cuit_cliente TEXT,
                razon_social TEXT,
                items_json TEXT, 
                referencia_factura TEXT,
                cae TEXT,
                vto_cae TEXT
            )
        """)
        print("[CREATED] Table 'remitos' created with 'referencia_factura'.")
    else:
        # Check for referencia_factura
        cursor.execute("PRAGMA table_info(remitos)")
        cols = [c[1] for c in cursor.fetchall()]
        
        if "referencia_factura" not in cols:
            print("Adding column: referencia_factura")
            cursor.execute("ALTER TABLE remitos ADD COLUMN referencia_factura TEXT")
        else:
            print("Column referencia_factura already exists.")

    conn.commit()
    conn.close()
    print("[SUCCESS] Database evolution complete.")

if __name__ == "__main__":
    evolve_db()
