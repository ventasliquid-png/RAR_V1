import fitz  # PyMuPDF
import re
import json
import logging

logging.basicConfig(level=logging.INFO, format="[SABUESO-ARCA] %(message)s")

def extraer_datos_factura(pdf_path: str, cuit_emisor: str = None) -> dict:
    """
    Infiltra un PDF de ARCA/AFIP, extrae los bloques de texto coordinados
    para sortear el desorden espacial de AFIP, y apresa los datos vitales.
    
    Retorna JSON con:
    - cuit_receptor
    - comprobante (Pto Vta - Factura)
    - cae
    - vto_cae
    """
    datos_extraidos = {
        "cuit_receptor": None,
        "comprobante": None,
        "cae": None,
        "vto_cae": None,
        "error": None
    }
    
    try:
        doc = fitz.open(pdf_path)
        
        # Extracción por bloques ordenados espacialmente (Mejor que texto crudo para AFIP)
        text_blocks = []
        for page in doc:
            blocks = page.get_text("blocks")
            # Ordenamos por Y (arriba a abajo) y luego X (izq a der)
            blocks.sort(key=lambda b: (b[1], b[0]))
            for b in blocks:
                text_blocks.append(b[4].replace("\n", " ").strip())
        
        doc.close()
        texto_completo = " | ".join(text_blocks)

        # 1. CUIT RECEPTOR (Blindaje Nike/Almirante)
        patrones_cuit = re.findall(r'\b((?:20|23|24|27|30|33|34)\-?\d{8}\-?\d{1})\b', texto_completo)
        cuits_limpios = [c.replace("-", "") for c in patrones_cuit]
        
        if cuit_emisor:
            # Filtramos nuestro propio CUIT. El que sobra es el del cliente.
            cuits_filtrados = [c for c in cuits_limpios if c != cuit_emisor]
            if cuits_filtrados:
                datos_extraidos["cuit_receptor"] = cuits_filtrados[0]
        else:
            # Fallback por si no pasamos el CUIT emisor
            if len(cuits_limpios) >= 2:
                datos_extraidos["cuit_receptor"] = cuits_limpios[1]
            elif len(cuits_limpios) == 1:
                datos_extraidos["cuit_receptor"] = cuits_limpios[0]

        # 2. COMPROBANTE
        # Buscar "Punto de Venta: 00001 Comp Nro: 00002487" espaciado
        match_comp = re.search(r'Punto\s*de\s*Ventas?[^\d]*(\d{4,5}).*?Comp.*?(?:Nro)?[^\d]*(\d{8})', texto_completo, re.IGNORECASE)
        if not match_comp:
            # Fallback a "00001-00002487" crudo
            match_comp = re.search(r'(\d{4,5})\s*-\s*(\d{8})', texto_completo)

        if match_comp:
            datos_extraidos["comprobante"] = f"{match_comp.group(1).zfill(5)}-{match_comp.group(2).zfill(8)}"

        # 3. CAE
        match_cae = re.search(r'C\.?A\.?E\.?.*?(?:\:)?.*?(\d{14})', texto_completo, re.IGNORECASE)
        if match_cae:
            datos_extraidos["cae"] = match_cae.group(1)

        # 4. VENCIMIENTO CAE
        match_vto = re.search(r'(?:Vto|Vencimiento).*?(\d{2}/\d{2}/\d{4})', texto_completo, re.IGNORECASE)
        if match_vto:
            datos_extraidos["vto_cae"] = match_vto.group(1)

        if not datos_extraidos["cae"] or not datos_extraidos["cuit_receptor"]:
            datos_extraidos["error"] = "CRÍTICO: Faltan datos vitales (CAE o CUIT)."

    except Exception as e:
        datos_extraidos["error"] = f"Falla catastrófica: {str(e)}"
        
    return datos_extraidos

if __name__ == "__main__":
    import sys
    # CUIT de la Emisora (Sonido Liquido por defecto)
    cuit_nuestro = "30715603973" 
    
    ruta = sys.argv[1] if len(sys.argv) > 1 else "factura_prueba.pdf"
    logging.info(f"Iniciando Sabueso sobre: {ruta}")
    
    resultado = extraer_datos_factura(ruta, cuit_emisor=cuit_nuestro)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))
