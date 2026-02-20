import os, sys
from Conexion_Blindada import obtener_token

def audit_services():
    services = ["ws_sr_padron_a4", "ws_sr_padron_a5", "ws_sr_padron_a10", "ws_sr_padron_a13", "wsmtxca", "wsfe"]
    print(f"=== AUDITORÍA DE SERVICIOS AUTORIZADOS ===")
    
    for svc in services:
        print(f"[*] Probando: {svc}...", end=" ", flush=True)
        try:
            token, sign = obtener_token(svc)
            print("✅ AUTORIZADO")
        except Exception as e:
            if "Computador no autorizado" in str(e):
                print("❌ NO AUTORIZADO")
            else:
                print(f"⚠️ ERROR: {e}")

if __name__ == "__main__":
    audit_services()
