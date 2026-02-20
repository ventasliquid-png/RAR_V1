import sys
import os
from remito_engine import generar_remito_pdf
import remito_engine
print(f"DEBUG: Loaded remito_engine from {remito_engine.__file__}")

# Data extracted from "30715603973_001_00001_00002489 Lavimar.pdf"
cliente_data = {
    "razon_social": "LAVIMAR S A",
    "cuit": "30-53660291-3",
    "domicilio_fiscal": "Av.Cnel.Larrabure 2460 - Villa Maria, Córdoba",
    "condicion_iva": "RESPONSABLE INSCRIPTO",
    "factura_vinculada": "00001-00002489",
    "cae": "86084487042986",
    "vto_cae": "01/03/2026",
    "observaciones": "Documento generado a partir de Factura Electrónica."
}

items = [
    {
        "codigo": "SURG-BAC-1L", 
        "descripcion": "Surgibac PA botella 1 litro",
        "cantidad": 6.00,
        "unidad": "UN"
    }
]

# Output file
output_file = "REMITO_LAVIMAR_00002489_V2.pdf"

print(f"Generating Remito for {cliente_data['razon_social']}...")
# Using Mirrored Numbering: 0001-00002489 -> 00016-00002489
path = generar_remito_pdf(cliente_data, items, is_preview=False, output_path=output_file, numero_remito="00016-00002489")
print(f"SUCCESS: Generated {os.path.abspath(path)}")
