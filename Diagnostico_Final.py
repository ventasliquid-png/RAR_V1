import sys
import os
import subprocess
import base64
import re
from datetime import datetime, timedelta
from lxml import etree
from zeep import Client
from zeep.helpers import serialize_object
import logging

# === CONFIGURACIÓN ===
# === CONFIGURACIÓN ===
CUIT_PROPIO = 20132967572 
# Ajustá las rutas si es necesario
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(BASE_DIR, "certs", "certificado.crt")
KEY_PATH = os.path.join(BASE_DIR, "certs", "privada.key")
URL_WSAA = "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"
URL_PADRON = "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA13?wsdl"

logging.getLogger('zeep').setLevel(logging.ERROR)

def obtener_token():
    # Buscamos OpenSSL
    rutas = [r"C:\Program Files\Git\usr\bin\openssl.exe", r"C:\Program Files\Git\mingw64\bin\openssl.exe", r"C:\Windows\System32\openssl.exe"]
    openssl = next((r for r in rutas if os.path.exists(r)), None)
    
    if not openssl:
        print("[!] ERROR: OpenSSL no encontrado.")
        return None, None
    print(f"[*] OpenSSL detectado: {openssl}")

    now = datetime.now()
    tra = etree.Element("loginTicketRequest", version="1.0")
    h = etree.SubElement(tra, "header")
    etree.SubElement(h, "source").text = f"serialNumber=CUIT {CUIT_PROPIO},cn=rar_v5"
    etree.SubElement(h, "destination").text = "cn=wsaa,o=afip,c=ar,serialNumber=CUIT 33693450239"
    etree.SubElement(h, "uniqueId").text = str(int(now.timestamp()))
    etree.SubElement(h, "generationTime").text = (now - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(h, "expirationTime").text = (now + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(tra, "service").text = "ws_sr_padron_a13"
    
    print("[*] Generando TRA...")
    with open("temp_diag.xml", "wb") as f: f.write(etree.tostring(tra))
    
    print(f"[*] Firmando CMS con {CERT_PATH}...")
    try:
        subprocess.run(f'"{openssl}" cms -sign -in temp_diag.xml -out temp_diag.cms -signer "{CERT_PATH}" -inkey "{KEY_PATH}" -nodetach -outform DER', shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"[!] ERROR en OpenSSL: {e}")
        return None, None

    with open("temp_diag.cms", "rb") as f: cms = base64.b64encode(f.read()).decode()
    try: os.remove("temp_diag.xml"); os.remove("temp_diag.cms")
    except: pass
    
    print("[*] Conectando a WSAA (LoginCms)...")
    res = Client(URL_WSAA).service.loginCms(cms)
    print("[*] Token Obtenido!")
    xml = etree.fromstring(res.encode())
    return xml.find(".//token").text, xml.find(".//sign").text

def escanear(cuit_raw):
    cuit = re.sub(r'[^0-9]', '', str(cuit_raw))
    print(f"\n[*] Conectando a ARCA para escanear CUIT: {cuit}...")
    
    try:
        t, s = obtener_token()
        # Llamada SOAP
        res = Client(URL_PADRON).service.getPersona(t, s, CUIT_PROPIO, cuit)
        
        # Serializamos para que rar_core trabaje con diccionarios puros
        datos_dict = serialize_object(res)
        
        # --- DEBUG TEMPORAL ---
        try:
            print("\n[DEBUG] Keys de datos_dict:", datos_dict.keys())
            if 'personaReturn' in datos_dict:
                print(" -> personaReturn Keys:", datos_dict['personaReturn'].keys())
            elif 'persona' in datos_dict:
                 print(" -> persona Keys:", datos_dict['persona'].keys())
            else:
                 print(" -> Estructura desconocida.")
        except Exception as e:
            print(f"[DEBUG ERROR] {e}")

        # --- NUCLEO RAR V1 ---
        from rar_core import extraer_datos_completos
        resultado = extraer_datos_completos(datos_dict)
        
        if "error" in resultado:
            print(f"[!] Error: {resultado['error']}")
        else:
            print("\n" + "="*60)
            print(f" RESULTADO DEL ESCANEO FORENSE (RAR V1)")
            print("="*60)
            print(f" CUIT           : {resultado['cuit']}")
            print(f" RAZÓN SOCIAL   : {resultado['razon_social']}")
            print(f" CONDICIÓN IVA  : {resultado['condicion_iva']}")
            print(f" DOMICILIO      : {resultado['domicilio_fiscal']}")
            print("-" * 60)
            print(f" Debug Flags    : {resultado['raw_debug']}")
            print("="*60 + "\n")

    except Exception as e:
        print(f"[X] ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== DEBUG AUTO-RUN: 20132967572 ===")
    escanear(20132967572)