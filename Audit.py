import sqlite3
import os

def ver_cantera():
    db_path = "v5_cantera_oro.db"
    if not os.path.exists(db_path):
        print(f"[!] Error: No se encuentra la base de datos {db_path}")
        return

    conn = sqlite3.connect(db_path)
    
    print("\n" + "="*40)
    print("   REPORTE DE LA CANTERA ORO (V5)")
    print("="*40)

    # 1. Clientes
    print("\n[ CLIENTES MAPEADOS ]")
    clientes = conn.execute("SELECT alias_bas, cuit, razon_social_afip FROM clientes_mapeo").fetchall()
    if not clientes:
        print(" > No hay clientes cargados aún.")
    for c in clientes:
        print(f"Alias: {c[0]:<10} | CUIT: {c[1]:<13} | RS: {c[2]}")
    
    # 2. Productos
    print("\n[ PRODUCTOS VALIDADOS ]")
    prods = conn.execute("SELECT codigo_bas, desc_v5_oro, consistencia_flag FROM cantera_productos").fetchall()
    if not prods:
        print(" > No hay productos en la cantera.")
    for p in prods:
        estado = "OK (Oro)" if p[2] == 1 else "PENDIENTE"
        print(f"Cod: {p[0]:<10} | Desc: {p[1]:<30} | Estado: {estado}")

    conn.close()
    print("\n" + "="*40)
    input("\nPresione ENTER para cerrar esta ventana...")

if __name__ == "__main__":
    ver_cantera()