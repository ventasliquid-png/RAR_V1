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

def obtener_token():
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
    etree.SubElement(tra, "service").text = "ws_sr_padron_a13"
    
    # Archivos temporales con ruta absoluta para evitar problemas de CWD
    temp_xml = os.path.join(BASE_DIR, "temp_auth.xml")
    temp_cms = os.path.join(BASE_DIR, "temp_auth.cms")

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
    
    res = Client(URL_WSAA).service.loginCms(cms)
    xml = etree.fromstring(res.encode())
    return xml.find(".//token").text, xml.find(".//sign").text

def get_datos_afip(cuit_raw):
    """
    Consulta AFIP y devuelve un diccionario normalizado según rar_core.
    Retorna {'error': ...} en caso de fallo.
    """
    cuit = re.sub(r'[^0-9]', '', str(cuit_raw))
    if len(cuit) != 11:
        return {"error": "CUIT inválido (longitud incorrecta)"}

    try:
        token, sign = obtener_token()
        res = Client(URL_PADRON).service.getPersona(token, sign, CUIT_PROPIO, cuit)
        
        datos_dict = serialize_object(res)
        return extraer_datos_completos(datos_dict)
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("=== MÓDULO DE CONEXIÓN BLINDADA (TEST) ===")
    c = input("Ingrese CUIT: ").strip()
    if c:
        d = get_datos_afip(c)
        print(json.dumps(d, indent=4, ensure_ascii=False))