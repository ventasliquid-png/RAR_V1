import os
import time
import datetime
import base64
import requests
from zeep import Client
from zeep.transports import Transport

# --- HERRAMIENTAS DE FIRMA Y CIRUGÍA ---
from endesive import signer
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from asn1crypto import cms # <--- La herramienta para abrir el sobre

# ================= CONFIGURACIÓN =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(BASE_DIR, "certs", "certificado.crt")
KEY_PATH  = os.path.join(BASE_DIR, "certs", "privada.key")

CUIT_EMISOR = "20132967572" # Carlos Paturzo

# URLs Oficiales
WSAA_WSDL = "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"
PADRON_WSDL = "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA13?wsdl"
# =================================================

def generar_ticket_xml(servicio="ws_sr_padron_a13"):
    """Genera el XML de solicitud (TRA)"""
    now = datetime.datetime.now()
    expiration = now + datetime.timedelta(minutes=720)
    
    # Formato simple que le gusta a AFIP (Local Time)
    def fmt(d): return d.strftime("%Y-%m-%dT%H:%M:%S")
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <loginTicketRequest version="1.0">
        <header>
            <uniqueId>{int(time.time())}</uniqueId>
            <generationTime>{fmt(now - datetime.timedelta(minutes=10))}</generationTime>
            <expirationTime>{fmt(expiration)}</expirationTime>
        </header>
        <service>{servicio}</service>
    </loginTicketRequest>
    """
    return xml.encode('utf-8')

def firmar_y_encapsular(xml_data):
    """
    1. Firma con endesive (genera CMS detached/desconectado).
    2. Usa asn1crypto para inyectar el XML adentro (Attached/Adjunto).
    """
    print("[*] Procesando llaves...")
    with open(KEY_PATH, 'rb') as f:
        key = serialization.load_pem_private_key(f.read(), None, default_backend())
    with open(CERT_PATH, 'rb') as f:
        cert = x509.load_pem_x509_certificate(f.read(), default_backend())
        
    print("[*] Generando firma base...")
    # Firmamos (esto crea la estructura criptográfica válida pero vacía de contenido)
    # attrs=True agrega la fecha de firma (requerido por AFIP)
    signature_der = signer.sign(xml_data, key, cert, [], 'sha1', attrs=True)
    
    print("[*] Realizando cirugía de encapsulado (Attached)...")
    # 1. Cargamos la estructura CMS
    info = cms.ContentInfo.load(signature_der)
    signed_data = info['content']
    
    # 2. Inyectamos el XML en el campo 'encap_content_info'
    # Esto transforma la firma Detached en Attached
    signed_data['encap_content_info']['content'] = xml_data
    
    # 3. Volvemos a empaquetar
    final_der = info.dump()
    return final_der

def conectar_arca():
    print("=========================================")
    print(" CONEXIÓN NATIVA: EL RE-ENCAPSULADO")
    print("=========================================")
    
    try:
        # 1. PREPARAR EL PAQUETE BLINDADO
        tra_xml = generar_ticket_xml()
        cms_firmado = firmar_y_encapsular(tra_xml)
        cms_b64 = base64.b64encode(cms_firmado).decode('utf-8')

        # 2. ENVIAR A ARCA (WSAA)
        print("[*] Enviando sobre a WSAA (Login)...")
        session = requests.Session()
        session.verify = True 
        transport = Transport(session=session)
        
        client_wsaa = Client(WSAA_WSDL, transport=transport)
        response = client_wsaa.service.loginCms(cms_b64)
        
        # 3. LEER RESPUESTA
        from xml.etree import ElementTree
        root = ElementTree.fromstring(response)
        token = root.find(".//token").text
        sign = root.find(".//sign").text
        
        print(f"\n[OK] ¡SE ABRIÓ EL CIELO! Token recibido.")
        print(f"     Clave: {token[:15]}...")
        
        return token, sign

    except Exception as e:
        print(f"\n[X] Error en Login: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print("     Respuesta del servidor:", e.response.content)
        return None, None

def consultar_padron(token, sign):
    """Buscamos a ANTAPHARMA"""
    cuit_objetivo = "20330663731" 
    print(f"\n[*] Consultando CUIT: {cuit_objetivo}...")
    
    try:
        transport = Transport(session=requests.Session())
        client_padron = Client(PADRON_WSDL, transport=transport)
        
        consulta = {
            'token': token,
            'sign': sign,
            'cuitRepresentada': CUIT_EMISOR,
            'idPersona': cuit_objetivo
        }
        
        res = client_padron.service.getPersona(**consulta)
        
        if res and 'personaReturn' in res:
            p = res['personaReturn']
            if 'datosGenerales' in p:
                dg = p['datosGenerales']
                nombre = dg.get('razonSocial') or f"{dg.get('apellido', '')} {dg.get('nombre', '')}"
                
                print("\n" + "="*50)
                print("         ¡VICTORIA TOTAL!")
                print("="*50)
                print(f" CLIENTE:      {nombre.strip()}")
                print(f" DIRECCIÓN:    {p.get('datosDomicilio', {}).get('direccion', 'No informado')}")
                print(f" ESTADO CLAVE: {dg.get('estadoClave', 'N/A')}")
                print("="*50)
            else:
                print("[!] CUIT existe pero sin datos públicos.")
        else:
            print("[!] No hay datos para este CUIT.")
            
    except Exception as e:
        print(f"[X] Error en Padrón: {e}")

if __name__ == "__main__":
    t, s = conectar_arca()
    if t and s:
        consultar_padron(t, s)