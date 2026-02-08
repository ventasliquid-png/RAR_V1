import sqlite3
import os
import glob
import json
from Conexion_Blindada import get_datos_afip

# === CONFIGURACIÓN ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "cantera_arca.db")

def inicializar_cantera():
    """
    Crea la estructura de tablas para la 'Fuente de Verdad' de ARCA.
    Diseñada para soportar Emisión Automática de Remitos.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. TABLA MAESTRA DE CLIENTES (Validada por ARCA)
    # Fundamental para el encabezado del remito (Fiscal) y logística (Sucursales)
    cursor.execute('''CREATE TABLE IF NOT EXISTS cantera_clientes (
                        cuit TEXT PRIMARY KEY,
                        razon_social TEXT,
                        condicion_iva TEXT,
                        domicilio_fiscal TEXT,
                        sucursales_json TEXT
                    )''')

    # 2. TABLA DE MAPEO LEGACY (El puente con BAS)
    # Permite que el sistema viejo 'hable' con el nuevo sin tocar el viejo.
    cursor.execute('''CREATE TABLE IF NOT EXISTS mapeo_legacy (
                        id_bas TEXT PRIMARY KEY,
                        cuit_referencia TEXT,
                        FOREIGN KEY(cuit_referencia) REFERENCES cantera_clientes(cuit)
                    )''')

    # 3. TABLA DE PRODUCTOS (Normalizados para ARCA)
    # 'bandera_on_off' define si el producto se informa o se ignora en el remito.
    cursor.execute('''CREATE TABLE IF NOT EXISTS cantera_productos (
                        id_producto TEXT PRIMARY KEY,
                        nombre_arca TEXT,
                        bandera_on_off INTEGER DEFAULT 1
                    )''')

    conn.commit()
    conn.close()
    print(f"[*] Base de datos '{DB_NAME}' inicializada y alineada para emisión.")

def buscar_o_cosechar_cliente(conn, id_bas, razon_social_bas):
    """
    Busca el CUIT en el mapeo local. Si no existe, inicia el protocolo de Cosecha
    para obtener datos oficiales de ARCA.
    """
    cursor = conn.cursor()
    
    # 1. ¿Ya lo tenemos mapeado?
    res = cursor.execute("SELECT cuit_referencia FROM mapeo_legacy WHERE id_bas = ?", (id_bas,)).fetchone()
    if res:
        return res[0] # Retorna el CUIT ya conocido
    
    # 2. Si no, necesitamos intervención Humana o Inteligente
    print(f"\n[!] CLIENTE NUEVO DETECTADO: {id_bas} - {razon_social_bas}")
    cuit_input = input(f"    >> Ingrese CUIT para '{razon_social_bas}': ").strip()
    
    if not cuit_input:
        print("    [X] Omitido.")
        return None

    # 3. Verificar si el CUIT ya está en la Cantera
    res_cuit = cursor.execute("SELECT razon_social FROM cantera_clientes WHERE cuit = ?", (cuit_input,)).fetchone()
    
    if res_cuit:
        print(f"    [OK] CUIT ya existente en Cantera ({res_cuit[0]}). Vinculando...")
    else:
        # 4. COSECHA DE ARCA (Conexión Blindada)
        print(f"    [*] Consultando ARCA para CUIT {cuit_input}...")
        datos_afip = get_datos_afip(cuit_input)
        
        if "error" in datos_afip:
            print(f"    [X] Error crítico en ARCA: {datos_afip['error']}")
            return None
        
        # 5. Persistir datos frescos de ARCA
        print(f"    [V] Validado: {datos_afip['razon_social']} ({datos_afip['condicion_iva']})")
        
        sucursales_default = json.dumps([{"id": 1, "direccion": datos_afip['domicilio_fiscal'], "alias": "Fiscal"}])
        
        cursor.execute("INSERT OR REPLACE INTO cantera_clientes (cuit, razon_social, condicion_iva, domicilio_fiscal, sucursales_json) VALUES (?, ?, ?, ?, ?)",
                       (datos_afip['cuit'], datos_afip['razon_social'], datos_afip['condicion_iva'], datos_afip['domicilio_fiscal'], sucursales_default))
    
    # 6. Crear el vinculo Legacy -> CUIT
    cursor.execute("INSERT OR REPLACE INTO mapeo_legacy (id_bas, cuit_referencia) VALUES (?, ?)", (id_bas, cuit_input))
    conn.commit()
    
    return cuit_input

def procesar_reporte():
    """
    Lee REPORTE 2.TXT y alimenta la Cantera ARCA.
    """
    # Buscamos en el directorio del script
    patron = os.path.join(BASE_DIR, "REPORTE 2*")
    archivos = glob.glob(patron)
    if not archivos:
        print(f"[!] No se encontró REPORTE 2.TXT en {BASE_DIR}")
        return
    
    archivo_nombre = archivos[0]
    print(f"[*] Procesando lote: {archivo_nombre}")
    
    conn = sqlite3.connect(DB_NAME)
    
    try:
        with open(archivo_nombre, 'r', encoding='latin-1') as f:
            lineas = f.readlines()
            
        for i, linea in enumerate(lineas):
            linea = linea.strip()
            if not linea: continue
            
            # Limpieza básica de formato BAS
            if "]" in linea:
                linea = linea.split("] ", 1)[-1] if "] " in linea else linea.split("]", 1)[-1]

            datos = [d.strip().replace('"', '') for d in linea.split(",")]
            if len(datos) < 10: continue

            id_bas = datos[2]
            razon = datos[3]
            item_cod = datos[7]
            item_desc = datos[8]
            
            # FASE 1: CLIENTES
            cuit_validado = buscar_o_cosechar_cliente(conn, id_bas, razon)
            
            # FASE 2: PRODUCTOS
            if cuit_validado and item_cod:
               res_prod = conn.execute("SELECT nombre_arca FROM cantera_productos WHERE id_producto = ?", (item_cod,)).fetchone()
               if not res_prod:
                   # Auto-sembrado de productos (Por defecto validos, bandera 1)
                   # En el futuro, esto podría pedir confirmación si la descripción es muy críptica
                   conn.execute("INSERT INTO cantera_productos (id_producto, nombre_arca, bandera_on_off) VALUES (?, ?, 1)", (item_cod, item_desc))
                   conn.commit()
                   # print(f"    [P] Producto nuevo registrado: {item_cod}")

    except Exception as e:
        print(f"[X] Excepción global: {e}")
    finally:
        conn.close()
    
    print("\n[*] Lote procesado. La Cantera ARCA ha sido actualizada.")

if __name__ == "__main__":
    inicializar_cantera()
    procesar_reporte()