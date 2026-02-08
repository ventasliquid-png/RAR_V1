import json

def extraer_datos_completos(json_afip):
    """
    Extrae y normaliza datos de la respuesta de AFIP (getPersona),
    implementando la lógica de '3 Cajones' para determinar la Condición de IVA.
    """
    # Manejo de la estructura de respuesta que puede variar levemente
    datos = {}
    if 'personaReturn' in json_afip:
        datos = json_afip['personaReturn']
    elif 'persona' in json_afip:
        datos = json_afip['persona']
    else:
        # Intento de fallback si se pasa el diccionario interno directamente
        datos = json_afip

    generales = datos.get('datosGenerales', {})
    if not generales:
        # Fallback: Verificar si los datos generales están en la raíz (flattened)
        if 'razonSocial' in datos or 'apellido' in datos or 'idPersona' in datos:
             generales = datos
        else:
            return {
                "error": "No se encontraron datos generales (estructura inválida)"
            }

    # --- Lógica de los "3 Cajones" para Condición IVA ---
    iva_status = "CONSUMIDOR FINAL" # Default safe
    regimen_general = datos.get('datosRegimenGeneral')
    monotributo = datos.get('datosMonotributo')

    if regimen_general:
        # Busca en la lista de impuestos el código de IVA
        impuestos = regimen_general.get('impuesto', [])
        if not isinstance(impuestos, list): impuestos = [impuestos]
        
        es_ri = False
        es_exento = False
        
        for imp in impuestos:
            id_imp = imp.get('idImpuesto')
            if id_imp == 30: # IVA
                es_ri = True
            elif id_imp == 32: # IVA Exento
                es_exento = True
                
        if es_ri:
            iva_status = "RESPONSABLE INSCRIPTO"
        elif es_exento:
            iva_status = "EXENTO"
                
    elif monotributo:
        # El nodo monotributo suele implicar que es Monotributista
        # Se puede extraer la categoría si se desea: monotributo.get('categoriaMonotributo', {}).get('descripcionCategoria')
        iva_status = "MONOTRIBUTISTA"

    # --- Extracción de Domicilio Fiscal ---
    domicilio_fiscal_str = ""
    domicilio = generales.get('domicilioFiscal', {})
    if domicilio:
        direccion = domicilio.get('direccion', '')
        localidad = domicilio.get('localidad', '')
        provincia = domicilio.get('descripcionProvincia', '')
        cod_postal = domicilio.get('codPostal', '')
        domicilio_fiscal_str = f"{direccion}, {localidad}, {provincia} ({cod_postal})".strip()

    # --- Construcción del Resultado ---
    razon_social = generales.get('razonSocial')
    if not razon_social:
        apellido = generales.get('apellido', '')
        nombre = generales.get('nombre', '')
        razon_social = f"{apellido} {nombre}".strip()

    return {
        "cuit": generales.get('idPersona'),
        "razon_social": razon_social,
        "domicilio_fiscal": domicilio_fiscal_str,
        "condicion_iva": iva_status,
        "raw_debug": { # Para depuración si hace falta
            "es_monotributo": bool(monotributo),
            "es_regimen_general": bool(regimen_general)
        }
    }
