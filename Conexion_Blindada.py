import sys, os, subprocess, base64, re, json
from datetime import datetime, timedelta
from lxml import etree
from zeep import Client
from zeep.helpers import serialize_object
from rar_core import extraer_datos_completos

# === CONFIGURACIÓN ===
CUIT_PROPIO = 20132967572 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(BASE_DIR, "certs", "certificado.crt")
KEY_PATH = os.path.join(BASE_DIR, "certs", "privada.key")
URL_WSAA = "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"
URL_PADRON = "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA13?wsdl"
URL_WSMTXCA = "https://serviciosjava.afip.gov.ar/wsmtxca/services/MTXCAService?wsdl"
LOG_PATH = os.path.join(BASE_DIR, "arca_trace.log")

def log_arca_trace(tipo, datos):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] [{tipo}] {json.dumps(datos, default=str)}\n")

def obtener_token(service="ws_sr_padron_a13"):
    rutas = [r"C:\Program Files\Git\usr\bin\openssl.exe", r"C:\Program Files\Git\mingw64\bin\openssl.exe", r"C:\Windows\System32\openssl.exe"]
    openssl = next((r for r in rutas if os.path.exists(r)), None)
    
    if not openssl:
        raise Exception("OpenSSL no encontrado en rutas estándar.")

    now = datetime.now()
    tra = etree.Element("loginTicketRequest", version="1.0")
    h = etree.SubElement(tra, "header")
    etree.SubElement(h, "source").text = f"serialNumber=CUIT {CUIT_PROPIO},cn=rar_v5"
    etree.SubElement(h, "destination").text = "cn=wsaa,o=afip,c=ar,serialNumber=CUIT 33693450239"
    etree.SubElement(h, "uniqueId").text = str(int(now.timestamp()))
    etree.SubElement(h, "generationTime").text = (now - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(h, "expirationTime").text = (now + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(tra, "service").text = service
    
    # Archivos temporales con ruta absoluta para evitar problemas de CWD
    temp_xml = os.path.join(BASE_DIR, f"temp_auth_{service}.xml")
    temp_cms = os.path.join(BASE_DIR, f"temp_auth_{service}.cms")

    with open(temp_xml, "wb") as f: f.write(etree.tostring(tra))
    
    try:
        subprocess.run(f'"{openssl}" cms -sign -in "{temp_xml}" -out "{temp_cms}" -signer "{CERT_PATH}" -inkey "{KEY_PATH}" -nodetach -outform DER', shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        if os.path.exists(temp_xml): os.remove(temp_xml)
        raise Exception("Error firmando solicitud con OpenSSL.")

    with open(temp_cms, "rb") as f: cms = base64.b64encode(f.read()).decode()
    
    try: 
        if os.path.exists(temp_xml): os.remove(temp_xml)
        if os.path.exists(temp_cms): os.remove(temp_cms)
    except: pass
    
    log_arca_trace("TRA_REQ", {"service": service, "uniqueId": str(int(now.timestamp()))})
    
    res = Client(URL_WSAA).service.loginCms(cms)
    xml = etree.fromstring(res.encode())
    
    token = xml.find(".//token").text
    sign = xml.find(".//sign").text
    
    log_arca_trace("TRA_RES", {"service": service, "token_len": len(token)})
    return token, sign

def get_datos_afip(cuit_raw):
    """
    Consulta AFIP y devuelve un diccionario normalizado según rar_core.
    Retorna {'error': ...} en caso de fallo.
    """
    cuit = re.sub(r'[^0-9]', '', str(cuit_raw))
    if len(cuit) != 11:
        return {"error": "CUIT inválido (longitud incorrecta)"}

    try:
        token, sign = obtener_token("ws_sr_padron_a13")
        
        log_arca_trace("PADRON_REQ", {"cuit": cuit})
        res = Client(URL_PADRON).service.getPersona(token, sign, CUIT_PROPIO, cuit)
        log_arca_trace("PADRON_RES", {"status": "ok"}) # No logueamos todo el payload por privacidad/tamaño
        
        datos_dict = serialize_object(res)
        return extraer_datos_completos(datos_dict)
        
    except Exception as e:
        log_arca_trace("PADRON_ERR", {"error": str(e)})
        return {"error": str(e)}

def solicitar_cae(remito_data):
    """
    STUB: Simula el envío a WSMTXCA y devuelve un CAE simulado si todo está bien.
    En Fase 3 se implementará la conexión real SOAP.
    """
    log_arca_trace("WSMTXCA_REQ_STUB", remito_data)
    
    # Simulación de respuesta exitosa
    import random
    cae = f"74{random.randint(100000000000, 999999999999)}"
    vto = (datetime.now() + timedelta(days=10)).strftime("%Y%m%d")
    
    log_arca_trace("WSMTXCA_RES_STUB", {"cae": cae, "vto": vto})
    
    return {"cae": cae, "vto_cae": vto, "resultado": "A"}

if __name__ == "__main__":
    print("=== MÓDULO DE CONEXIÓN BLINDADA (TEST) ===")
    c = input("Ingrese CUIT: ").strip()
    if c:
        d = get_datos_afip(c)
        print(json.dumps(d, indent=4, ensure_ascii=False))
