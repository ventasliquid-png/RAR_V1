import sys
import os
import json
from zeep.helpers import serialize_object
from Conexion_Blindada import obtener_token, URL_PADRON, CUIT_PROPIO
from zeep import Client

def debug_afip(cuit_objetivo):
    print(f"--- DEBUG RAW AFIP: {cuit_objetivo} ---")
    try:
        token, sign = obtener_token()
        client = Client(URL_PADRON)
        res = client.service.getPersona(token, sign, CUIT_PROPIO, cuit_objetivo)
        
        datos_dict = serialize_object(res)
        print(json.dumps(datos_dict, indent=4, default=str))
        
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    cuit = "30581050301" # El CUIT problemático
    debug_afip(cuit)
