import os
import sys
import subprocess
import base64
from datetime import datetime, timedelta
from lxml import etree
from zeep import Client

# === CONFIGURACIÓN ===
CUIT_PROPIO = 20132967572
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(BASE_DIR, "certs", "certificado.crt")
KEY_PATH = os.path.join(BASE_DIR, "certs", "privada.key")

# Rutas de Servicio de Autenticación (WSAA)
URL_WSAA_HOMO = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"
URL_WSAA_PROD = "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"

# Rutas de Servicio de Padrón (PersonaServiceA13) - Dummy endpoints for now, we just test Auth
URL_PADRON_HOMO = "https://awshomo.afip.gov.ar/sr-padron/webservices/personaServiceA13?wsdl"
URL_PADRON_PROD = "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA13?wsdl"

def obtener_token(url_wsaa, service="ws_sr_padron_a13"):
    print(f"--- Intentando autenticar con {url_wsaa} ---")
    
    # 1. Buscar OpenSSL
    rutas = [r"C:\Program Files\Git\usr\bin\openssl.exe", r"C:\Program Files\Git\mingw64\bin\openssl.exe", r"C:\Windows\System32\openssl.exe"]
    openssl = next((r for r in rutas if os.path.exists(r)), None)
    
    if not openssl:
        print("[ERROR] OpenSSL no encontrado.")
        return None

    # 2. Generar TRA
    now = datetime.now()
    tra = etree.Element("loginTicketRequest", version="1.0")
    h = etree.SubElement(tra, "header")
    etree.SubElement(h, "source").text = f"serialNumber=CUIT {CUIT_PROPIO},cn=rar_v5"
    etree.SubElement(h, "destination").text = "cn=wsaa,o=afip,c=ar,serialNumber=CUIT 33693450239"
    etree.SubElement(h, "uniqueId").text = str(int(now.timestamp()))
    etree.SubElement(h, "generationTime").text = (now - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(h, "expirationTime").text = (now + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(tra, "service").text = service
    
    temp_xml = os.path.join(BASE_DIR, "temp_auth_test.xml")
    temp_cms = os.path.join(BASE_DIR, "temp_auth_test.cms")

    try:
        with open(temp_xml, "wb") as f: f.write(etree.tostring(tra))
        
        # 3. Firmar TRA
        cmd = f'"{openssl}" cms -sign -in "{temp_xml}" -out "{temp_cms}" -signer "{CERT_PATH}" -inkey "{KEY_PATH}" -nodetach -outform DER'
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        with open(temp_cms, "rb") as f: cms = base64.b64encode(f.read()).decode()
        
        # 4. Llamar a WSAA
        client = Client(url_wsaa)
        res = client.service.loginCms(cms)
        xml = etree.fromstring(res.encode())
        
        token = xml.find(".//token").text
        sign = xml.find(".//sign").text
        
        print(f"[OK] Autenticación exitosa. Token length: {len(token)}")
        return token, sign
        
    except subprocess.CalledProcessError as e:
        print(f"[FALLO] Error OpenSSL: {e}")
    except Exception as e:
        print(f"[FALLO] Error General: {e}")
    finally:
        if os.path.exists(temp_xml): os.remove(temp_xml)
        if os.path.exists(temp_cms): os.remove(temp_cms)
    
    return None

def main():
    print("=== TEST DE SUPERVIVENCIA RAR V1 ===")
    print(f"Certificado: {CERT_PATH}")
    print(f"Clave Privada: {KEY_PATH}")
    
    if not os.path.exists(CERT_PATH):
        print(f"[CRITICAL] No se encuentra el certificado en {CERT_PATH}")
        return
    if not os.path.exists(KEY_PATH):
        print(f"[CRITICAL] No se encuentra la clave privada en {KEY_PATH}")
        return

    print("\n--- TEST 1: SANDBOX (Homologación) ---")
    token_homo = obtener_token(URL_WSAA_HOMO)
    
    print("\n--- TEST 2: PRODUCCIÓN ---")
    token_prod = obtener_token(URL_WSAA_PROD)
    
    print("\n=== RESULTADO DIAGNÓSTICO ===")
    if token_prod:
        print("✅ EL CERTIFICADO ES VÁLIDO PARA PRODUCCIÓN.")
        print(">> MODO OPERATIVO: REAL")
    elif token_homo:
        print("⚠️ EL CERTIFICADO ES VÁLIDO SOLO PARA SANDBOX.")
        print(">> MODO OPERATIVO: PRUEBA (NO LEGAL)")
    else:
        print("❌ EL CERTIFICADO NO SIRVE O ESTÁ VENCIDO.")
        print(">> ACCIÓN REQUERIDA: Generar nuevo CSR y tramitar en AFIP.")

if __name__ == "__main__":
    main()
