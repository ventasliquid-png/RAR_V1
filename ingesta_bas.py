import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "v5_cantera_oro.db")

def ingestar_item(item_raw):
    """
    Busca item_raw en cantera_productos.
    Si existe: retorna datos (descripción, unidad, sku).
    Si no existe: pide unidad_medida (input) y lo crea.
    """
    item_raw = item_raw.strip().upper()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Buscar coincidencia exacta (por ahora)
        cursor.execute("SELECT desc_v5_oro, unidad_medida, sku_v5 FROM cantera_productos WHERE desc_bas_ultima = ? OR desc_v5_oro = ?", (item_raw, item_raw))
        resultado = cursor.fetchone()

        if resultado:
            desc, unidad, sku = resultado
            print(f"[✅ ENCONTRADO] {desc} (Unidad: {unidad}) [SKU: {sku}]")
            return {"descripcion": desc, "unidad": unidad, "sku": sku}
        else:
            print(f"[⚠️ NUEVO] El ítem '{item_raw}' no existe en la Cantera.")
            
            # Modo interactivo para alta
            unidad = input(f"Ingrese Unidad de Medida para '{item_raw}' (ej: un, kg, m): ").strip().lower()
            if not unidad: unidad = "un"
            
            # Generar SKU temporal o null (V5 lo asignará después)
            sku = "TEMP-" + item_raw[:3]
            
            # Insertar en cantera
            try:
                cursor.execute("""
                    INSERT INTO cantera_productos (desc_bas_ultima, desc_v5_oro, sku_v5, unidad_medida, consistencia_flag)
                    VALUES (?, ?, ?, ?, 1)
                """, (item_raw, item_raw, sku, unidad))
                conn.commit()
                print(f"[💾 GUARDADO] Solidez agregada a Cantera de Oro.")
                return {"descripcion": item_raw, "unidad": unidad, "sku": sku}
            except Exception as e:
                print(f"[ERROR] No se pudo guardar: {e}")
                return None
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== MÓDULO TOMÁS: INGESTA & CONSISTENCIA ===")
    while True:
        i = input("\nIngrese Ítem (o 'salir'): ")
        if i.lower() in ['salir', 'exit']: break
        if not i: continue
        
        ingestar_item(i)
