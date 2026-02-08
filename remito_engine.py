from fpdf import FPDF
import unittest
import os

class PDFRemito(FPDF):
    def header(self):
        # Logo placeholder
        # self.image('logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'REMITO', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Página ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generar_remito_pdf(cliente_data, items, output_path="remito_test.pdf"):
    """
    Genera un archivo PDF con formato de Remito R.
    cliente_data: dict con 'razon_social', 'cuit', 'domicilio', etc.
    items: lista de dicts con 'codigo', 'descripcion', 'cantidad'.
    """
    pdf = PDFRemito()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    # --- CABECERA CLIENTE ---
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 10, f"Cliente: {cliente_data.get('razon_social', 'N/A')}", 0, 1, 'L', 1)
    pdf.cell(0, 10, f"CUIT: {cliente_data.get('cuit', 'N/A')}", 0, 1, 'L')
    pdf.cell(0, 10, f"Domicilio: {cliente_data.get('domicilio', 'N/A')}", 0, 1, 'L')
    pdf.cell(0, 10, f"Condición IVA: {cliente_data.get('condicion_iva', 'Consumidor Final')}", 0, 1, 'L')
    
    pdf.ln(10)
    
    # --- TABLA DE ITEMS ---
    # Encabezados
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(30, 10, 'Código', 1)
    pdf.cell(120, 10, 'Descripción', 1)
    pdf.cell(30, 10, 'Cant.', 1)
    pdf.ln()
    
    # Datos
    pdf.set_font('Arial', '', 12)
    for item in items:
        pdf.cell(30, 10, str(item.get('codigo', '')), 1)
        pdf.cell(120, 10, str(item.get('descripcion', '')), 1)
        pdf.cell(30, 10, str(item.get('cantidad', 0)), 1)
        pdf.ln()
        
    pdf.output(output_path)
    print(f"[*] PDF Generado: {output_path}")
    return output_path

class TestRemitoEngine(unittest.TestCase):
    def test_generacion_simple(self):
        cli = {
            "razon_social": "JUAN PEREZ",
            "cuit": "20-12345678-9",
            "domicilio": "CALLE FALSA 123",
            "condicion_iva": "RESPONSABLE INSCRIPTO"
        }
        items = [
            {"codigo": "P001", "descripcion": "Gaseosa Cola 2L", "cantidad": 10},
            {"codigo": "P002", "descripcion": "Sifón 1L", "cantidad": 5}
        ]
        path = generar_remito_pdf(cli, items, "test_output.pdf")
        self.assertTrue(os.path.exists(path))
        # Limpieza
        # os.remove(path)

if __name__ == '__main__':
    # Si se ejecuta directo, corre tests
    unittest.main()
