
import os
import json
import time
import shutil
from datetime import datetime
from Conexion_Blindada import solicitar_cae
from remito_arca_engine import generar_remito_pdf

# CONFIGURACIÓN
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COLA_DIR = os.path.join(BASE_DIR, "cola_envios")
ENVIADOS_DIR = os.path.join(BASE_DIR, "enviados")
ERROR_DIR = os.path.join(BASE_DIR, "errores_envio")

# Asegurar directorios
for d in [COLA_DIR, ENVIADOS_DIR, ERROR_DIR]:
    os.makedirs(d, exist_ok=True)

def procesar_cola():
    print(f"=== PROCESADOR DE COLA DE REMITOS ===")
    print(f"Directorio de Cola: {COLA_DIR}")
    
    archivos = [f for f in os.listdir(COLA_DIR) if f.endswith(".json")]
    
    if not archivos:
        print("✅ No hay remitos pendientes en la cola.")
        return

    print(f"🔄 Se encontraron {len(archivos)} remitos pendientes.")
    
    for archivo in archivos:
        path_archivo = os.path.join(COLA_DIR, archivo)
        print(f"\n>> Procesando: {archivo}...")
        
        try:
            with open(path_archivo, "r", encoding="utf-8") as f:
                remito_data = json.load(f)
            
            # Intentar Autorizar
            # IMPORTANTE: Forzamos pto_vta correcto si ya lo tenemos, o usamos el del JSON
            # Si el JSON tiene 'pto_vta': 5 (viejo), y ahora tenemos el 10, hay que actualizarlo?
            # Por ahora confiamos en el JSON o en la logica de Conexion_Blindada.
            
            resultado = solicitar_cae(remito_data)
            
            if resultado.get("cae"):
                # ÉXITO
                cae = resultado["cae"]
                vto = resultado["vto_cae"]
                print(f"   ✅ AUTORIZADO! CAE: {cae}")
                
                # 1. Generar PDF Final
                remito_data["cae"] = cae
                remito_data["vto_cae"] = vto
                remito_data["qr_url"] = resultado.get("qr_url")
                
                # Nombre PDF: REMITO_[PuntoVenta]_[Numero].pdf
                pv = str(remito_data.get('pto_vta', 0)).zfill(4) # WSMTXCA usually 4 or 5 digits? Con 5 es standard.
                nro = str(resultado.get('numero_comprobante', 0)).zfill(8)
                pdf_name = f"REMITO_{pv}_{nro}.pdf"
                pdf_path = os.path.join(ENVIADOS_DIR, pdf_name)
                
                generar_remito_pdf(remito_data, pdf_path)
                print(f"   📄 PDF Generado: {pdf_path}")
                
                # 2. Mover JSON a Enviados
                shutil.move(path_archivo, os.path.join(ENVIADOS_DIR, archivo))
                print("   📂 Archivado en /enviados")
                
            else:
                # FALLO AFIP
                error_msg = resultado.get("error", "Error desconocido")
                print(f"   ❌ RECHAZADO: {error_msg}")
                # Decisión: ¿Mover a errores o dejar en cola?
                # Si es error 1500 (PV incorrecto), dejarlo en cola hasta arreglar PV.
                # Si es error de validación de datos, mover a error.
                
                # Por seguridad, dejamos en cola para reintento manual o corrección.
                # O podríamos renombrarlo a .err para no trabar el loop?
                # Renombramos a .json_err
                # new_path = path_archivo + "_err"
                # shutil.move(path_archivo, new_path)
                
        except Exception as e:
            print(f"   ⚠️ ERROR CRÍTICO PROCESANDO ARCHIVO: {e}")
            # Mover a carpeta de errores para no bloquear
            shutil.move(path_archivo, os.path.join(ERROR_DIR, archivo))

if __name__ == "__main__":
    procesar_cola()
