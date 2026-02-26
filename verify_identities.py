from Conexion_Blindada import obtener_token, get_datos_afip, URL_WSAA
import json

def test_service(service_name):
    print(f"\n--- Probando servicio: {service_name} ---")
    try:
        token, sign, cuit = obtener_token(service_name)
        print(f"[OK] Handshake exitoso")
        print(f"     CUIT Firmante: {cuit}")
        print(f"     Token (prefix): {token[:15]}...")
        return True
    except Exception as e:
        print(f"[X] Error: {e}")
        return False

print("=== VERIFICACIÓN DE IDENTIDAD DUAL AFIP ===")

# 1. Probar Padrón (Identidad Personal)
suc_padron = test_service("ws_sr_padron_a13")

# 2. Probar Remitos (Identidad Empresa)
# Usamos 'wsmtxca' para forzar la identidad 'fiscal'
suc_fiscal = test_service("wsmtxca")

if suc_padron:
    print("\n[*] Validando consulta de datos reales (Lácteos de Poblet)...")
    try:
        # CUIT de Lácteos de Poblet: 30536602913 (según logs previos)
        datos = get_datos_afip("30536602913")
        if "error" not in datos:
            print(f"[V] Padrón Funcional: {datos.get('razon_social')}")
        else:
            print(f"[X] Error en Padrón: {datos['error']}")
    except Exception as e:
        print(f"[X] Excepción en Padrón: {e}")

if suc_padron and suc_fiscal:
    print("\n[RESUMEN] AMBAS IDENTIDADES OPERATIVAS.")
else:
    print("\n[RESUMEN] FALLA EN UNA O AMBAS IDENTIDADES.")
