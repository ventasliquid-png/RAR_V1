import os, sys
from Conexion_Blindada import obtener_token, URL_WSAA
from lxml import etree
from zeep import Client
from datetime import datetime, timedelta
import base64

# TEST IDENTITY: 20132967572
CUIT_2013 = 20132967572
CERT_2013 = "certs/certificado_06_02_2026.crt"
KEY_2013 = "certs/privada.key"
OPENSSL = r"C:\Program Files\Git\usr\bin\openssl.exe"

def get_token_custom(service):
    now = datetime.now()
    tra = etree.Element("loginTicketRequest", version="1.0")
    h = etree.SubElement(tra, "header")
    etree.SubElement(h, "source").text = f"serialNumber=CUIT {CUIT_2013},cn=RAR_V5"
    etree.SubElement(h, "destination").text = "cn=wsaa,o=afip,c=ar,serialNumber=CUIT 33693450239"
    etree.SubElement(h, "uniqueId").text = str(int(now.timestamp()))
    etree.SubElement(h, "generationTime").text = (now - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(h, "expirationTime").text = (now + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(tra, "service").text = service
    
    with open("temp.xml", "wb") as f: f.write(etree.tostring(tra))
    os.system(f'"{OPENSSL}" cms -sign -in temp.xml -out temp.cms -signer {CERT_2013} -inkey {KEY_2013} -nodetach -outform DER')
    
    with open("temp.cms", "rb") as f: cms = base64.b64encode(f.read()).decode()
    res = Client(URL_WSAA).service.loginCms(cms)
    xml = etree.fromstring(res.encode())
    return xml.find(".//token").text, xml.find(".//sign").text

def test():
    services = ["ws_sr_padron_a13", "wsmtxca"]
    print(f"=== AUDITORÍA IDENTIDAD 2013 ===")
    for svc in services:
        print(f"[*] Probando {svc}...", end=" ", flush=True)
        try:
            get_token_custom(svc)
            print("✅ OK")
        except Exception as e:
            print(f"❌ FAIL: {e}")

if __name__ == "__main__":
    test()
