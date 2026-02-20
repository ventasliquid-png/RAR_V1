
import sys
import os
from datetime import datetime
from zeep import Client
from Conexion_Blindada import obtener_token, CUIT_PROPIO

# URL WSFEv1 Produccion
URL_WSFE = "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"

def debug_wsfe():
    print(f"=== DEBUG WSFEv1 (Factura Electronica) ===")
    print(f"URL: {URL_WSFE}")
    
    try:
        print("\n1. Obteniendo Token (wsfe)...")
        token, sign = obtener_token("wsfe")
        print(f"   [OK] Token obtained.")
        
        client = Client(URL_WSFE)
        service = client.service
        
        auth = {'Token': token, 'Sign': sign, 'Cuit': CUIT_PROPIO}
        
        PV = 8
        print(f"\n2. Consultando Ultimo Comprobante (PV: {PV}, Tipo: 1 - Factura A)...")
        
        # FECompUltimoAutorizado(Auth, PtoVta, CbteTipo)
        ultimo = service.FECompUltimoAutorizado(auth, PV, 1)
        
        print("\n--- RESPUESTA ---")
        print(ultimo)
        
        if ultimo.Errors:
             print("\n❌ ERRORES:")
             for e in ultimo.Errors.Err:
                 print(f"   Code: {e.Code}, Msg: {e.Msg}")
        else:
             print(f"\n✅ EXITOSO. Ultimo Nro Factura A: {ultimo.CbteNro}")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {str(e)}")

if __name__ == "__main__":
    debug_wsfe()
