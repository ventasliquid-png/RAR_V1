import sqlite3
import os

DB_PATH = "C:\\dev\\RAR_V1\\v5_cantera_oro.db"

def upgrade_schema():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Upgrade cantera_productos (Add SKU)
        print("Checking cantera_productos...")
        cursor.execute("PRAGMA table_info(cantera_productos)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'sku' not in columns:
            print("Adding 'sku' column to cantera_productos...")
            cursor.execute("ALTER TABLE cantera_productos ADD COLUMN sku INTEGER")
        else:
            print("'sku' column already exists.")

        if 'codigo' not in columns:
            print("Adding 'codigo' column to cantera_productos...")
            cursor.execute("ALTER TABLE cantera_productos ADD COLUMN codigo TEXT")
        else:
            print("'codigo' column already exists.")

        if 'precio' not in columns:
            print("Adding 'precio' column to cantera_productos...")
            cursor.execute("ALTER TABLE cantera_productos ADD COLUMN precio REAL") # Or value?
        else:
            print("'precio' column already exists.")

        if 'descripcion' not in columns:
            print("Adding 'descripcion' column to cantera_productos...")
            cursor.execute("ALTER TABLE cantera_productos ADD COLUMN descripcion TEXT")
            print("Backfilling 'descripcion' from 'desc_v5_oro'...")
            cursor.execute("UPDATE cantera_productos SET descripcion = desc_v5_oro WHERE descripcion IS NULL")
        else:
            print("'descripcion' column already exists.")

        # 2. Upgrade cantera_clientes (Add codigo_interno)
        print("Checking cantera_clientes...")
        cursor.execute("PRAGMA table_info(cantera_clientes)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'codigo_interno' not in columns:
            print("Adding 'codigo_interno' column to cantera_clientes...")
            cursor.execute("ALTER TABLE cantera_clientes ADD COLUMN codigo_interno INTEGER")
        else:
            print("'codigo_interno' column already exists.")
            
        conn.commit()
        print("Schema upgrade completed successfully.")
        
    except Exception as e:
        print(f"Error upgrading schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_schema()
