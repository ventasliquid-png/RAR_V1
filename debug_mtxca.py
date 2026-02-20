
import sys
import os
import re
from datetime import datetime
from zeep import Client
from Conexion_Blindada import obtener_token, URL_WSMTXCA, CUIT_PROPIO

def debug_afip():
    print(f"=== ESCANER DE PUNTOS DE VENTA (WSMTXCA) ===")
    print(f"Buscando un PV habilitado para Remitos (Tipo 91)...")
    
    try:
        token, sign = obtener_token("wsmtxca")
        client = Client(URL_WSMTXCA)
        service = client.service
        auth = {'token': token, 'sign': sign, 'cuitRepresentada': CUIT_PROPIO}

        for pv in [16]: # Target PV 16 specifically
            print(f"\n>> Probando Punto de Venta {pv}...")
            try:
                consulta = {'codigoTipoComprobante': 91, 'numeroPuntoVenta': pv}
                ultimo = service.consultarUltimoComprobanteAutorizado(
                    authRequest=auth,
                    consultaUltimoComprobanteAutorizadoRequest=consulta
                )
                
                if hasattr(ultimo, 'arrayErrores') and ultimo.arrayErrores:
                    err = ultimo.arrayErrores.codigoDescripcion[0]
                    print(f"   [X] Falló: {err.descripcion} (Cod {err.codigo})")
                else:
                    print(f"   [¡ENCONTRADO!] ✅ El PV {pv} FUNCIONA para Remitos!")
                    print(f"   Último comprobante: {ultimo.numeroComprobante}")
                    return # Stop on first success
            except Exception as e:
                print(f"   [Error Técnico] {str(e)}")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {str(e)}")

if __name__ == "__main__":
    debug_afip()
