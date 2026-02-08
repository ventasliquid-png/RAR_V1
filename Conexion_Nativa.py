import base64
from datetime import datetime, timedelta
from lxml import etree
from zeep import Client
from endesive import signer
from cryptography.hazmat.primitives import serialization
from cryptography import x509
import logging

# ==========================================
# CONFIGURACIÓN (CA - CASA)
# ==========================================
CUIT_PROPIO = 20132967572 
CERT_PATH = "certs/certificado.crt"
KEY_PATH = "certs/privada.key"

# Producción
URL_WSAA = "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"
URL_PADRON = "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA13?wsdl"

logging.getLogger('zeep').setLevel(logging.ERROR)

def obtener_token_wsaa():
    print("[*] Generando Ticket (TRA)...")
    # Formato de tiempo exacto que le gusta a ARCA
    now = datetime.now()
    generation_time = now - timedelta(minutes=10)
    expiration_time = now + timedelta(minutes=10)
    
    tra = etree.Element("loginTicketRequest", version="1.0")
    header = etree.SubElement(tra, "header")
    etree.SubElement(header, "source").text = str(CUIT_PROPIO)
    etree.SubElement(header, "destination").text = "cn=wsaa,o=afip,c=ar,serialNumber=CUIT 33693450239"
    etree.SubElement(header, "uniqueId").text = str(int(now.timestamp()))
    etree.SubElement(header, "generationTime").text = generation_time.strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(header, "expirationTime").text = expiration_time.strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(tra, "service").text = "ws_sr_padron_a13"
    
    tra_xml = etree.tostring(tra, encoding="UTF-8")

    print("[*] Firmando solicitud...")
    with open(KEY_PATH, "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    with open(CERT_PATH, "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read())

    # CORRECCIÓN VITAL:
    # Usamos solo los argumentos necesarios. 
    # Al no poner 'False', la librería incluye los atributos de tiempo (signingTime) automáticamente.
    datos_firmados = signer.sign(tra_xml, key, cert, [], 'sha256')
    
    cms_b64 = base64.b64encode(datos_firmados).decode('utf-8')

    print("[*] Autenticando en WSAA...")
    client = Client(wsdl=URL_WSAA)
    return client.service.loginCms(cms_b64)

def consultar_padron(cuit_objetivo):
    try:
        xml_res = obtener_token_wsaa()
        login_response = etree.fromstring(xml_res.encode('utf-8'))
        token = login_response.find(".//token").text
        sign = login_response.find(".//sign").text
        print(f"[OK] ¡Token recibido! Puerta abierta.")
        
        print(f"[*] Buscando datos para: {cuit_objetivo}...")
        client = Client(wsdl=URL_PADRON)
        res = client.service.getPersona(
            token=token,
            sign=sign,
            cuitRepresentada=CUIT_PROPIO,
            idPersona=cuit_objetivo
        )

        print("\n" + "="*40 + "\n RESPUESTA DE ARCA \n" + "="*40)
        # Imprimimos de forma segura para evitar errores de codificación
        print(res)
        
        if res and 'personaReturn' in res and 'datosGenerales' in res['personaReturn']:
            d = res['personaReturn']['datosGenerales']
            razon = d.get('razonSocial', '')
            nombre = f"{d.get('apellido', '')} {d.get('nombre', '')}".strip()
            print(f"\n[!] RESULTADO FINAL: {razon if razon else nombre}")
        
    except Exception as e:
        print(f"\n[X] ERROR: {e}")

if __name__ == "__main__":
    print("="*41 + "\n SISTEMA RAR_V1: CONEXIÓN NATIVA \n" + "="*41)
    # Probamos con tu CUIT para el debut
    consultar_padron(20132967572)