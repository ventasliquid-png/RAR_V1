import os
import sys

# Agregar el directorio actual al path para importar Conexion_Blindada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

try:
    from Conexion_Blindada import obtener_token, URL_WSAA
    print(f"[*] Probando conexión con: {URL_WSAA}")
    print("[*] Solicitando Token y Sign...")
    token, sign, cuit = obtener_token("ws_sr_padron_a13")
    print(f"[OK] Token obtenido (len: {len(token)})")
    print(f"    Token: {token[:10]}...")
    print(f"    Sign:  {sign[:10]}...")
    
    # Probar Padrón
    from Conexion_Blindada import get_datos_afip
    print("\n[*] Consultando get_datos_afip(30715603973)...")
    datos = get_datos_afip("30715603973")
    print("\n[V] RESPUESTA PADRON:")
    print(datos)
    
except Exception as e:
    print("\n[X] FALLO EL HANDSHAKE:")
    print(f"    Error: {str(e)}")
    import traceback
    traceback.print_exc()
