
import sys
from zeep import Client
from Conexion_Blindada import obtener_token, URL_WSMTXCA, CUIT_PROPIO

def probe_pv8():
    print(f"=== SONDA DE DIAGNOSTICO PV 0008 ===")
    
    try:
        # 1. Get WSMTXCA Token (We know this works)
        token, sign = obtener_token("wsmtxca")
        client = Client(URL_WSMTXCA)
        service = client.service
        auth = {'token': token, 'sign': sign, 'cuitRepresentada': CUIT_PROPIO}
        
        PV = 9
        
        # TEST A: Remito (Type 91)
        print(f"\n[TEST A] Consultando Remito (91) en PV {PV}...")
        try:
            r91 = service.consultarUltimoComprobanteAutorizado(
                authRequest=auth,
                consultaUltimoComprobanteAutorizadoRequest={'codigoTipoComprobante': 91, 'numeroPuntoVenta': PV}
            )
            if hasattr(r91, 'arrayErrores') and r91.arrayErrores:
                print(f"   ❌ Resultado: RECHAZADO ({r91.arrayErrores.codigoDescripcion[0].codigo})")
            else:
                 print(f"   ✅ Resultado: EXITO (Ult: {r91.numeroComprobante})")
        except Exception as e:
            print(f"   ⚠️ Error Tecnico: {e}")

        # TEST B: Factura A (Type 1)
        print(f"\n[TEST B] Consultando Factura A (1) en PV {PV}...")
        try:
            r1 = service.consultarUltimoComprobanteAutorizado(
                authRequest=auth,
                consultaUltimoComprobanteAutorizadoRequest={'codigoTipoComprobante': 1, 'numeroPuntoVenta': PV}
            )
            if hasattr(r1, 'arrayErrores') and r1.arrayErrores:
                print(f"   ❌ Resultado: RECHAZADO ({r1.arrayErrores.codigoDescripcion[0].codigo})")
            else:
                 print(f"   ✅ Resultado: EXITO (Ult: {r1.numeroComprobante})")
        except Exception as e:
             print(f"   ⚠️ Error Tecnico: {e}")

        # TEST C: Remito Carnico (Type 997) - Just to check if it's the wrong system
        print(f"\n[TEST C] Consultando Remito Carnico (997) en PV {PV}...")
        try:
            r997 = service.consultarUltimoComprobanteAutorizado(
                authRequest=auth,
                consultaUltimoComprobanteAutorizadoRequest={'codigoTipoComprobante': 997, 'numeroPuntoVenta': PV}
            )
            if hasattr(r997, 'arrayErrores') and r997.arrayErrores:
                print(f"   ❌ Resultado: RECHAZADO ({r997.arrayErrores.codigoDescripcion[0].codigo})")
            else:
                 print(f"   ✅ Resultado: EXITO (Ult: {r997.numeroComprobante}) - ¡ES UN PV CARNICO!")
        except Exception as e:
             print(f"   ⚠️ Error Tecnico: {e}")

             
    except Exception as e:
        print(f"\n[CRITICAL] Error de Token/Conexion: {str(e)}")

if __name__ == "__main__":
    probe_pv8()
