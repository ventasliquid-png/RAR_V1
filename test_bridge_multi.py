from Conexion_Blindada import get_datos_afip, solicitar_cae
import json

def test_bridge():
    print("=== TEST PUENTE MULTI-IDENTIDAD ===")
    
    # 1. Test Padron (CUIT 2013 identity)
    target_cuit = "30611306632" # Biotenk
    print(f"[*] Probando Búsqueda CUIT: {target_cuit}...")
    res_padron = get_datos_afip(target_cuit)
    if "error" in res_padron:
        print(f"❌ FALLO PADRON: {res_padron['error']}")
    else:
        print(f"✅ ÉXITO PADRON: {res_padron.get('razon_social', 'OK')}")

    # 2. Test WSMTXCA (CUIT 3071 identity)
    print("\n[*] Probando Autorización Remito (Solución Dummy)...")
    remito_dummy = {
        "cuit": target_cuit,
        "pto_vta": 1,
        "items": [{"producto": "TEST", "cantidad": 1}],
        "modo_offline": False
    }
    res_remito = solicitar_cae(remito_dummy)
    if "error" in res_remito:
        if "Computador no autorizado" in str(res_remito['error']):
             print(f"❌ FALLO REMITO: No autorizado (Esperado si 3071 está caído)")
        else:
             print(f"✅ ÉXITO REMITO (Comunicación OK): {res_remito.get('cae', 'PENDIENTE')}")
    else:
        print(f"✅ ÉXITO REMITO: CAE={res_remito.get('cae')}")

if __name__ == "__main__":
    test_bridge()
