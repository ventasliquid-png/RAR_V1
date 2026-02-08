import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "cantera_arca.db")

if not os.path.exists(DB_NAME):
    print(f"[!] DB not found at {DB_NAME}")
else:
    conn = sqlite3.connect(DB_NAME)
    print("\n[ CLIENTES ]")
    for r in conn.execute("SELECT * FROM cantera_clientes"): print(r)
    
    print("\n[ MAPEO LEGACY ]")
    for r in conn.execute("SELECT * FROM mapeo_legacy"): print(r)
    
    print("\n[ PRODUCTOS ]")
    for r in conn.execute("SELECT * FROM cantera_productos"): print(r)
    conn.close()
