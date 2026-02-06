import sqlite3
import os
import glob

DB_NAME = "v5_cantera_oro.db"

def inicializar_cantera():
    conn = sqlite3.connect(DB_NAME)
    # 5 Columnas definidas
    conn.execute('''CREATE TABLE IF NOT EXISTS cantera_productos 
                 (codigo_bas TEXT PRIMARY KEY, desc_bas_ultima TEXT, 
                  desc_v5_oro TEXT, sku_v5 TEXT, consistencia_flag INTEGER)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS clientes_mapeo 
                 (alias_bas TEXT PRIMARY KEY, cuit TEXT, razon_social_afip TEXT)''')
    conn.commit()
    conn.close()

def procesar_reporte():
    archivos = glob.glob("REPORTE 2*")
    if not archivos:
        print("[!] No se encontró el archivo REPORTE 2.TXT")
        return
    
    archivo_nombre = archivos[0]
    print(f"[*] Procesando: {archivo_nombre}")
    
    conn = sqlite3.connect(DB_NAME)
    with open(archivo_nombre, 'r', encoding='latin-1') as f:
        lineas = f.readlines()
    
    for i, linea in enumerate(lineas):
        linea = linea.strip()
        if not linea: continue
        if "]" in linea:
            linea = linea.split("] ", 1)[-1] if "] " in linea else linea.split("]", 1)[-1]

        datos = [d.strip().replace('"', '') for d in linea.split(",")]
        if len(datos) < 10: continue

        try:
            alias = datos[2]
            razon = datos[3]
            item_cod = datos[7]
            item_desc = datos[8]
            if not item_cod: continue

            # 1. Validación de Cliente (Ya funciona perfecto)
            res_cli = conn.execute("SELECT cuit FROM clientes_mapeo WHERE alias_bas = ?", (alias,)).fetchone()
            if not res_cli:
                print(f"\n[!] CLIENTE NUEVO: {alias}")
                cuit = input(f"    Ingrese CUIT para '{razon}': ").strip()
                if cuit:
                    conn.execute("INSERT INTO clientes_mapeo VALUES (?, ?, ?)", (alias, cuit, razon))
                    conn.commit()

            # 2. Validación de Producto (PARCHE APLICADO AQUÍ)
            res_prod = conn.execute("SELECT desc_bas_ultima FROM cantera_productos WHERE codigo_bas = ?", (item_cod,)).fetchone()
            if not res_prod:
                print(f"\n>>> Detectado: {alias} | Item: {item_cod}")
                print(f"    Desc. BAS: {item_desc}")
                opcion = input("    ¿Correcto para V5? (S/N o escriba la nueva): ")
                desc_oro = item_desc if opcion.upper() == 'S' else opcion
                
                # Usamos 5 placeholders (?) para las 5 columnas
                conn.execute("INSERT INTO cantera_productos VALUES (?, ?, ?, ?, ?)", 
                             (item_cod, item_desc, desc_oro, item_cod, 1))
                conn.commit()
                print(f"    [OK] Producto {item_cod} sembrado.")

        except Exception as e:
            print(f"[!] Error en línea {i+1}: {e}")
            
    conn.close()
    print("\n[*] Fin del proceso.")

if __name__ == "__main__":
    inicializar_cantera()
    procesar_reporte()