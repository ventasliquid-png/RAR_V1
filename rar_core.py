import json

def extraer_datos_completos(json_afip):
    """
    Extrae y normaliza datos de la respuesta de AFIP (getPersona A13),
    adaptada a la estructura real del servicio.
    """
    datos = {}
    
    # 1. Navegación Segura por la Estructura
    if 'personaReturn' in json_afip:
        datos = json_afip['personaReturn'].get('persona', {})
    elif 'persona' in json_afip:
        datos = json_afip['persona']
    else:
        datos = json_afip

    if not datos:
        return {"error": "Estructura de respuesta AFIP vacía o inválida."}

    # 2. Extracción de Razón Social / Nombre
    razon_social = datos.get('razonSocial')
    if not razon_social:
        apellido = datos.get('apellido', '')
        nombre = datos.get('nombre', '')
        razon_social = f"{apellido} {nombre}".strip()
    
    # 3. Extracción de Domicilio (Búsqueda de FISCAL)
    domicilio_fiscal_str = "SIN DOMICILIO FISCAL"
    domicilios = datos.get('domicilio', [])
    if not isinstance(domicilios, list): domicilios = [domicilios]

    # Prioridad: FISCAL > LEGAL/REAL > Primero que encuentre
    dom_fiscal = next((d for d in domicilios if d.get('tipoDomicilio') == 'FISCAL'), None)
    if not dom_fiscal:
        dom_fiscal = next((d for d in domicilios if d.get('tipoDomicilio') == 'LEGAL/REAL'), None)
    if not dom_fiscal and domicilios:
        dom_fiscal = domicilios[0]

    if dom_fiscal:
        direccion = dom_fiscal.get('direccion', '')
        localidad = dom_fiscal.get('localidad') or ''
        provincia = dom_fiscal.get('descripcionProvincia') or ''
        cod_postal = dom_fiscal.get('codigoPostal') or ''
        domicilio_fiscal_str = f"{direccion}, {localidad}, {provincia} ({cod_postal})".strip()
        # Limpieza de comas y espacios extra
        domicilio_fiscal_str = domicilio_fiscal_str.replace(", ,", ",").replace(" ,", "")

    # 4. Inferencia de Condición IVA
    # A13 a veces no trae 'impuestos' si consultamos con clave ajena restringida.
    # Usamos heurística: Si es SA/SRL -> RI. Si no, Consumidor Final (Fallback).
    
    iva_status = "CONSUMIDOR FINAL" # Default cauteloso
    
    # Intento 1: Impuestos explícitos (datosRegimenGeneral / monotributo)
    # Nota: A13 suele traer esto en datosRegimenGeneral, pero si falla...
    regimen_general = datos.get('datosRegimenGeneral')
    monotributo = datos.get('datosMonotributo')

    if monotributo:
        iva_status = "MONOTRIBUTISTA"
    elif regimen_general:
        impuestos = regimen_general.get('impuesto', [])
        if not isinstance(impuestos, list): impuestos = [impuestos]
        if any(i.get('idImpuesto') == 30 for i in impuestos):
            iva_status = "RESPONSABLE INSCRIPTO"
        elif any(i.get('idImpuesto') == 32 for i in impuestos):
             iva_status = "EXENTO"
    else:
        # Intento 2: Heurística por Forma Jurídica
        forma_juridica = datos.get('formaJuridica', '').upper()
        if "SOC. ANONIMA" in forma_juridica or "S.A." in forma_juridica or "S.R.L." in forma_juridica:
            iva_status = "RESPONSABLE INSCRIPTO"

    return {
        "cuit": str(datos.get('idPersona', '')),
        "razon_social": razon_social,
        "domicilio_fiscal": domicilio_fiscal_str,
        "condicion_iva": iva_status,
        "raw_debug": { 
             "formaJuridica": datos.get('formaJuridica'),
             "tipoPersona": datos.get('tipoPersona')
        }
    }
