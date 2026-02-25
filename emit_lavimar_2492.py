import sys
import os
from remito_engine import generar_remito_pdf

# Data extracted from "30715603973_001_00001_00002492 Lavimar.pdf"
cliente_data = {
    "razon_social": "LAVIMAR S A",
    "cuit": "30-53660291-3",
    "domicilio_fiscal": "Av.Cnel.Larrabure 2460 - Villa Maria, Córdoba",
    "condicion_iva": "RESPONSABLE INSCRIPTO",
    "factura_vinculada": "00001-00002492",
    "cae": "86085217820280",
    "vto_cae": "07/03/2026",
    "observaciones": "Documento generado a partir de Factura Electrónica.",
    "bultos": "1", # Standard fallback
    "valor_declarado": "0.0",
    "transporte": "PROPIO"
}

items = [
    {
        "codigo": "SURGI-PA-5L", 
        "descripcion": "Surgiibac PA bidon por 5 litros",
        "cantidad": 6.00,
        "unidad": "UN"
    }
]

# Output file
output_file = "REMITO_LAVIMAR_00002492_FINAL.pdf"

print(f"Generating Remito for {cliente_data['razon_social']}...")
# Mirrored Numbering: 0001-00002492 -> 0016-00002492 (As requested by Carlos)
path = generar_remito_pdf(cliente_data, items, is_preview=False, output_path=output_file, numero_remito="0016-00002492")
print(f"SUCCESS: Generated {os.path.abspath(path)}")
