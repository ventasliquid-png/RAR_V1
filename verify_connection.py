import os
import sys

# Agregar el directorio actual al path para importar Conexion_Blindada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

try:
    from Conexion_Blindada import obtener_token, URL_WSAA
    print(f"[*] Probando conexión con: {URL_WSAA}")
    print("[*] Solicitando Token y Sign...")
    token, sign = obtener_token()
    print("\n[V] HANDSHAKE EXITOSO!")
    print(f"    Token: {token[:10]}...")
    print(f"    Sign:  {sign[:10]}...")
except Exception as e:
    print("\n[X] FALLO EL HANDSHAKE:")
    print(f"    Error: {str(e)}")
    import traceback
    traceback.print_exc()
