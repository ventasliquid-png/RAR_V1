import sys
import os
from Conexion_Blindada import obtener_token, URL_WSMTXCA, CUIT_PROPIO
from zeep import Client

def test_connection():
    print("=== TEST CONEXIÓN AFIP WSFEv1 ===")
    
    # 0. Prueba Padron (Debería funcionar si el cert es valido)
    print("\n0. Solicitando Token (ws_sr_padron_a13)...")
    try:
        token_padron, sign_padron = obtener_token("ws_sr_padron_a13")
        print(f"[OK] Token Padron obtenido. Len={len(token_padron)}")
    except Exception as e:
        print(f"[ERROR] Falló autenticación Padron: {e}")

    # 1. Prueba de Autenticación WSMTXCA
    print("\n1. Solicitando Token (wsmtxca)...")
    try:
         token, sign = obtener_token("wsmtxca")
         print(f"✅ [EXITO] Token WSMTXCA obtenido. Len={len(token)}")
         print(">> AUTORIZADO! El servicio funciona.")
    except Exception as e:
         print(f"❌ [FALLO] {e}")
         print(">> COMPUTADOR NO AUTORIZADO (o servicio caído).")
         return
             
    # 2. Prueba de Servicio (Dummy call) - Solo si pasa autenticacion
    if 'token' in locals():
        print("\n2. Consultando Estado WSMTXCA (Dummy)...")
    # ... resto del código ...

    # 2. Prueba de Servicio (Dummy call)
    print("\n2. Consultando Último Comprobante (Pto Vta 1, Tipo 1)...")
    try:
        client = Client(URL_WSFEV1)
        service = client.service
        
        # Piquetero check: PtoVta 1, CbteTipo 1 (Factura A)
        response = service.FECompUltimoAutorizado(
            Auth={'Token': token, 'Sign': sign, 'Cuit': CUIT_PROPIO},
            PtoVta=1,
            CbteTipo=1
        )
        
        print(f"[OK] Último Comprobante Autorizado: {response.CbteNro}")
        print("Conexión Establecida y Funcional.")
        
    except Exception as e:
        print(f"[ERROR] Falló llamada al servicio: {e}")

if __name__ == "__main__":
    test_connection()
