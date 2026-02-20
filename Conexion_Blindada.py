import sys, os, subprocess, base64, re, json
from datetime import datetime, timedelta
from lxml import etree
from zeep import Client
from zeep.helpers import serialize_object
from rar_core import extraer_datos_completos

# === IDENTIDADES ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IDENTIDADES = {
    "padron": {
        "cuit": 20132967572,
        "cert": os.path.join(BASE_DIR, "certs", "certificado_06_02_2026.crt")
    },
    "fiscal": {
        "cuit": 30715603973,
        "cert": os.path.join(BASE_DIR, "certs", "certificado.crt")
    }
}
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
    # Selección de Identidad
    id_key = "padron" if "padron" in service else "fiscal"
    identity = IDENTIDADES[id_key]
    cuit_propio = identity["cuit"]
    cert_path = identity["cert"]

    rutas = [r"C:\Program Files\Git\usr\bin\openssl.exe", r"C:\Program Files\Git\mingw64\bin\openssl.exe", r"C:\Windows\System32\openssl.exe"]
    openssl = next((r for r in rutas if os.path.exists(r)), None)
    
    if not openssl:
        raise Exception("OpenSSL no encontrado en rutas estándar.")

    now = datetime.now()
    tra = etree.Element("loginTicketRequest", version="1.0")
    h = etree.SubElement(tra, "header")
    # Nota: El cn en source a veces es sensible, alternamos entre rar_v5 y RAR_V5 según cert
    cn_name = "RAR_V5" if id_key == "padron" else "rar_v5"
    etree.SubElement(h, "source").text = f"serialNumber=CUIT {cuit_propio},cn={cn_name}"
    etree.SubElement(h, "destination").text = "cn=wsaa,o=afip,c=ar,serialNumber=CUIT 33693450239"
    etree.SubElement(h, "uniqueId").text = str(int(now.timestamp()))
    etree.SubElement(h, "generationTime").text = (now - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(h, "expirationTime").text = (now + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S")
    etree.SubElement(tra, "service").text = service
    
    temp_xml = os.path.join(BASE_DIR, f"temp_auth_{service}.xml")
    temp_cms = os.path.join(BASE_DIR, f"temp_auth_{service}.cms")

    with open(temp_xml, "wb") as f: f.write(etree.tostring(tra))
    
    try:
        subprocess.run(f'"{openssl}" cms -sign -in "{temp_xml}" -out "{temp_cms}" -signer "{cert_path}" -inkey "{KEY_PATH}" -nodetach -outform DER', shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        if os.path.exists(temp_xml): os.remove(temp_xml)
        raise Exception(f"Error firmando solicitud {service} con certificado {cert_path}")

    with open(temp_cms, "rb") as f: cms = base64.b64encode(f.read()).decode()
    
    try: 
        if os.path.exists(temp_xml): os.remove(temp_xml)
        if os.path.exists(temp_cms): os.remove(temp_cms)
    except: pass
    
    log_arca_trace("TRA_REQ", {"service": service, "cuit": cuit_propio})
    
    res = Client(URL_WSAA).service.loginCms(cms)
    xml = etree.fromstring(res.encode())
    
    token = xml.find(".//token").text
    sign = xml.find(".//sign").text
    
    return token, sign, cuit_propio

def get_datos_afip(cuit_raw):
    """
    Consulta AFIP y devuelve un diccionario normalizado según rar_core.
    """
    cuit = re.sub(r'[^0-9]', '', str(cuit_raw))
    if len(cuit) != 11:
        return {"error": "CUIT inválido"}

    try:
        token, sign, cuit_propio = obtener_token("ws_sr_padron_a13")
        
        log_arca_trace("PADRON_REQ", {"cuit_target": cuit})
        res = Client(URL_PADRON).service.getPersona(token, sign, cuit_propio, cuit)
        
        datos_dict = serialize_object(res)
        return extraer_datos_completos(datos_dict)
        
    except Exception as e:
        log_arca_trace("PADRON_ERR", {"error": str(e)})
        return {"error": str(e)}

def calcular_totales(items):
    """
    Calcula neto, iva y total sumando items.
    Asume IVA 21% por defecto para simplificar Fase 2.
    """
    total = 0
    neto = 0
    iva = 0
    
    for item in items:
        # item: {'cantidad': '1', 'precio': 100.0, ...}
        # Asegurar tipos
        cant = float(item.get('cantidad', 1))
        precio = float(item.get('precio', 0.0))
        
        subtotal_linea = cant * precio
        
        # En AFIP: ImpTotal = ImpNeto + ImpIVA + ImpTrib + ImpOpEx
        # Asumimos que el precio en Cantera es NETO (sin IVA) o FINAL?
        # Para B2B (Resp Inscripto), precios suelen ser netos.
        # Asumimos Precio = Unitario Neto.
        
        neto_linea = subtotal_linea
        iva_linea = neto_linea * 0.21
        
        neto += neto_linea
        iva += iva_linea
        total += (neto_linea + iva_linea)
        
    return round(neto, 2), round(iva, 2), round(total, 2)

def solicitar_cae(remito_data):
    """
    Conecta a WSMTXCA (Remitos) y solicita CAE real para Remito Electrónico (Código 91).
    remito_data: {"cuit": 20..., "items": [...], "pto_vta": 5, "tipo_cbte": 91}
    """
    log_arca_trace("WSMTXCA_REQ_START", {"cuit_cliente": remito_data.get('cuit')})
    
    # MODO CONTINGENCIA / OFFLINE
    if remito_data.get('modo_offline') or remito_data.get('contingencia'):
        return guardar_en_cola(remito_data)
    
    
    try:
        # 1. Autenticación (servicio 'wsmtxca')
        token, sign = obtener_token("wsmtxca")
        
        # 2. Preparar Datos
        cuit_cliente = re.sub(r'[^0-9]', '', str(remito_data.get('cuit', '0')))
        pto_vta = int(remito_data.get('pto_vta', 7)) # Default 7 (MTXCA Web Services)
        tipo_cbte = int(remito_data.get('tipo_cbte', 91)) # 91: Remito Electrónico
        
        # WSMTXCA no requiere importes para Remitos (es traslado de mercadería), 
        # pero sí items. Vamos a ver si el servicio requiere 'importeTotal' = 0.
        # Según manual MTXCA: Remito (91) no lleva importes monetarios obligatorios, 
        # pero la estructura de items puede ser requerida.
        
        # 3. Conectar WSMTXCA
        client = Client(URL_WSMTXCA)
        service = client.service
        
        # 4. Obtener Último Comprobante Autorizado 
        # consultartUltimoComprobanteAutorizado(authRequest, consultaUltimoComprobanteAutorizadoRequest)
        ultimo_cmp = 0
        try:
            auth = {'token': token, 'sign': sign, 'cuitRepresentada': CUIT_PROPIO}
            consulta = {'codigoTipoComprobante': tipo_cbte, 'numeroPuntoVenta': pto_vta}
            
            ultimo = service.consultarUltimoComprobanteAutorizado(
                authRequest=auth,
                consultaUltimoComprobanteAutorizadoRequest=consulta
            )
            # WSMTXCA returns 'numeroComprobante'
            ultimo_cmp = ultimo.numeroComprobante or 0
        except Exception as e:
            log_arca_trace("WSMTXCA_LAST_CMP_ERR", {"error": str(e)})
            ultimo_cmp = 0

        proximo_cmp = ultimo_cmp + 1
        fecha_cbte = datetime.now().strftime("%Y-%m-%d") # Format YYYY-MM-DD for MTXCA? WSFE is YYYYMMDD.
        # Checking MTXCA documentation usually uses 'date' type or YYYY-MM-DD. Let's try YYYY-MM-DD.
        
        # 5. Armar Payload autorizarComprobante
        # Estructura: 
        # solicitud: {
        #   comprobanteCAERequest: {
        #     codigoTipoComprobante: 91,
        #     numeroPuntoVenta: 5,
        #     numeroComprobante: proximo_cmp,
        #     fechaEmision: '2023-10-27',
        #     codigoTipoDocumento: 80,
        #     numeroDocumento: cuit_cliente,
        #     importeTotal: 0, 
        #     arrayItems: { item: [...] }
        #   }
        # }
        
        items_payload = []
        for it in remito_data.get('items', []):
            items_payload.append({
                'unidadesMtx': int(float(it.get('cantidad', 1))),
                'codigoMtx': '0000000000000', 
                'codigo': 'TP001', # Dummy or internal code
                'descripcion': it.get('producto', 'Item'),
                'cantidad': float(it.get('cantidad', 1)),
                'codigoUnidadMedida': 7, # 7: Unidades
                'precioUnitario': 0.0,
                'importeBonificacion': 0.0,
                'codigoCondicionIVA': 1, # 1: IVA No Gravado (since Remito value is 0)
                'importeIVA': 0.0,
                'importeItem': 0.0
            })

        comprobante_request = {
            'codigoTipoComprobante': tipo_cbte,
            'numeroPuntoVenta': pto_vta,
            'numeroComprobante': proximo_cmp,
            'fechaEmision': fecha_cbte,
            'codigoTipoDocumento': 80,
            'numeroDocumento': int(cuit_cliente),
            'codigoConcepto': 1, # 1: Productos
            'importeTotal': 0,
            'importeSubtotal': 0,
            'codigoMoneda': 'PES',
            'cotizacionMoneda': 1,
            'arrayItems': {'item': items_payload}
        }
        
        log_arca_trace("WSMTXCA_PAYLOAD", comprobante_request)
        
        # 6. Llamada a AFIP
        response = service.autorizarComprobante(
            authRequest=auth,
            comprobanteCAERequest=comprobante_request
        )
        
        # 7. Procesar Respuesta
        res_dict = serialize_object(response)
        log_arca_trace("WSMTXCA_RESPONSE", res_dict)
        
        # Verificar errores
        if res_dict.get('arrayErrores'):
            errores = res_dict['arrayErrores']['codigoDescripcion']
            err_msg = "; ".join([f"{e['codigo']}: {e['descripcion']}" for e in errores])
            return {"error": f"AFIP Error: {err_msg}", "resultado": "R"}
            
        resultado = res_dict.get('resultado') # A (Aprobado), R (Rechazado), P (Parcial)
        
        if resultado == 'A':
            comprobante_resp = res_dict.get('comprobanteResponse')
            cae = comprobante_resp.get('cae')
            vto_cae = comprobante_resp.get('fechaVencimientoCAE') # YYYY-MM-DD
            
            # Normalizar Vto a YYYYMMDD para QR y PDF (o mantener formato date)
            # PDF engine expects string.
            if isinstance(vto_cae, datetime): # Zeep might convert dates
                vto_cae_str = vto_cae.strftime("%Y%m%d")
            else:
                vto_cae_str = str(vto_cae).replace("-", "")

            # Generar URL QR (Formato MTXCA puede diferir, usamos estándar FE)
            # URL = https://www.afip.gob.ar/fe/qr/?p=BASE64
            # JSON: "ctz" -> "cotiz" in some ver? Standard version 1.
            qr_json = {
                "ver": 1,
                "fecha": fecha_cbte.replace("-",""),
                "cuit": CUIT_PROPIO,
                "ptoVta": pto_vta,
                "tipoCmp": tipo_cbte,
                "nroCmp": proximo_cmp,
                "importe": 0,
                "moneda": "PES",
                "ctz": 1,
                "tipoDocRec": 80,
                "nroDocRec": int(cuit_cliente),
                "tipoCodAut": "E",
                "codAut": int(cae)
            }
            import base64
            qr_b64 = base64.b64encode(json.dumps(qr_json).encode()).decode()
            qr_url = f"https://www.afip.gob.ar/fe/qr/?p={qr_b64}"
            
            return {
                "cae": cae,
                "vto_cae": vto_cae_str,
                "resultado": "A",
                "qr_url": qr_url,
                "numero_comprobante": proximo_cmp
            }
        else:
            # Rechazado sin errores globales (observaciones en items?)
            obs = res_dict.get('arrayObservaciones')
            msg = "Rechazado"
            if obs:
                msg = str(obs)
            return {"error": msg, "resultado": resultado}

    except Exception as e:
        log_arca_trace("WSMTXCA_CRITICAL_ERR", {"error": str(e)})
        # SI FALLA LA CONEXIÓN O ES ERROR CRÍTICO, ¿GUARDAMOS EN COLA?
        # Por ahora devolvemos error y dejamos que la UI decida llamar a guardar_en_cola 
        # o que el usuario elija "Modo Offline" desde el principio.
        return {"error": str(e), "resultado": "E"}

def guardar_en_cola(remito_data):
    """
    Guarda el remito en la carpeta 'cola_envios' para procesamiento batch.
    Retorna estructura simulada de éxito (Pendiente).
    """
    COLA_DIR = os.path.join(BASE_DIR, "cola_envios")
    os.makedirs(COLA_DIR, exist_ok=True)
    
    # Generar ID único temporal
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cuit_cliente = remito_data.get('cuit', 'SN')
    filename = f"pendiente_{timestamp}_{cuit_cliente}.json"
    path = os.path.join(COLA_DIR, filename)
    
    # Agregar marca de tiempo
    remito_data['fecha_creacion_cola'] = timestamp
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(remito_data, f, indent=4, ensure_ascii=False)
            
        log_arca_trace("COLA_SAVE", {"file": filename})
        
        return {
            "cae": "PENDIENTE",
            "vto_cae": "PENDIENTE",
            "resultado": "Q", # Q de Queued
            "qr_url": "https://www.afip.gob.ar/fe/qr/?p=PENDIENTE",
            "numero_comprobante": 0,
            "motivo": "Guardado en Cola de Contingencia"
        }
    except Exception as e:
        return {"error": f"Error guardando en cola: {str(e)}", "resultado": "E"}

if __name__ == "__main__":
    print("=== MÓDULO DE CONEXIÓN BLINDADA (TEST) ===")
    c = input("Ingrese CUIT: ").strip()
    if c:
        d = get_datos_afip(c)
        print(json.dumps(d, indent=4, ensure_ascii=False))
