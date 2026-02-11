from fpdf import FPDF
import unittest
import os
from datetime import datetime
import textwrap

# Color Dominante: Azul Oscuro (#252b75) -> RGB (37, 43, 117)
COLOR_R = 37
COLOR_G = 43
COLOR_B = 117

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_IMAGE = os.path.join(BASE_DIR, "base_remito_v1.png")

class PDFRemito(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.is_preview = False
        self.copy_label = "ORIGINAL"
        self.copy_symbol = "*"
        self.remito_numero = None # Nuevo: Numero de Remito
    
    def header(self):
        # 1. Background Image (Full Page)
        if os.path.exists(BG_IMAGE):
            self.image(BG_IMAGE, x=0, y=0, w=210, h=297)
        
        # 2. Marca de Agua (VISTA PREVIA)
        if self.is_preview:
            self.set_font('Arial', 'B', 50)
            self.set_text_color(200, 200, 200)
            self.rotate(45, 105, 148)
            self.text(50, 190, "VISTA PREVIA - SIN VALIDEZ")
            self.rotate(0)
            
        # 3. Leyenda de Copia (Original, Dup, Trip)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(COLOR_R, COLOR_G, COLOR_B)
        # 4. Numero de Remito (NUEVO)
        # Posición: Caja Superior Derecha "REMITO Nº"
        # Ajuste: Desplazar 3 espacios abajo (aprox 12-15mm). Original Y=13 -> Y=25
        if self.remito_numero:
            self.set_xy(145, 25) 
            self.set_font('Arial', 'B', 16)
            self.set_text_color(COLOR_R, COLOR_G, COLOR_B)
            self.cell(50, 10, self.remito_numero, 0, 0, 'C')

        # 5. Leyenda Vertical Izquierda (Sobre-escribir imagen)
        # Tapamos lo viejo (Extendemos desde mitad de página)
        self.set_fill_color(255, 255, 255)
        self.rect(2, 120, 8, 170, 'F') 
        
        # 6. TAPAR FLORCITA ORIGINAL (Si existe en la plantilla base)
        # Asumimos que está cerca del pie o donde pusimos los nuevos símbolos.
        # Creamos un parche blanco en la zona inferior central.
        self.rect(80, 270, 50, 20, 'F') 

        # Escribimos lo nuevo (Rotado)
        self.set_font('Arial', '', 8)
        self.set_text_color(COLOR_R, COLOR_G, COLOR_B)
        self.rotate(90, 8, 280)
        self.text(8, 280, "* ORIGINAL   ** DUPLICADO   *** TRIPLICADO")
        self.rotate(0)

        # 7. Símbolos Nuevos (ZapfDingbats)
        # Asumimos posición inferior central o cerca del pie
        # IMPORTANTE: Desactivar auto_page_break para evitar recursión infinita
        # IMPORTANTE: Desactivar auto_page_break para evitar recursión infinita
        # ya que estamos escribiendo muy cerca del final de la página dentro del header.
        original_auto_page_break = self.auto_page_break
        self.set_auto_page_break(False)
        
        self.set_xy(0, 275)
        self.set_font('ZapfDingbats', '', 24) # Fuente de Símbolos
        self.cell(0, 10, self.copy_symbol, 0, 0, 'C')
        
        self.set_auto_page_break(original_auto_page_break, self.b_margin)

    def footer(self):
        # Pie de página manejado por coordenadas BAS (L60-62)
        pass

    def add_content(self, cliente_data, items):
        self.add_page()
        
        # --- CONFIGURACIÓN DE GRILLA BAS ---
        OFFSET_Y = 2  # Ajuste fino vertical top-margin
        OFFSET_X = 5  # Ajuste fino horizontal left-margin
        LH = 3.5      # Line Height
        CW = 2.2      # Char Width
        
        def set_bas_xy(line, col):
            x = OFFSET_X + (col * CW)
            y = OFFSET_Y + (line * LH)
            self.set_xy(x, y)

        # Configurar Fuente Principal
        self.set_text_color(0, 0, 0) # Negro
        self.set_font('Arial', 'B', 10) # Negrita para resaltar sobre fondo

        # --- ENCABEZADO ---
        
        # Fecha (L12, C71)
        set_bas_xy(12, 71) 
        fecha_str = datetime.now().strftime("%d/%m/%Y")
        self.cell(30, 6, fecha_str, 0)
        
        # Nombre (L18, C10)
        raw_nombre = str(cliente_data.get('razon_social', '')).upper()
        nombre_lines = textwrap.wrap(raw_nombre, 33)[:2] 
        
        for i, line_text in enumerate(nombre_lines):
            set_bas_xy(18 + i, 10)
            self.cell(80, 6, line_text, 0)
            
        # CUIT (L19, C52)
        set_bas_xy(19, 52)
        self.cell(40, 6, str(cliente_data.get('cuit', '')), 0)
        
        # IVA (L19, C71)
        set_bas_xy(19, 71) 
        cond_iva = str(cliente_data.get('condicion_iva', ''))
        if "INSCRIPTO" in cond_iva: cond_iva = "Resp. Inscripto"
        elif "CONSUMIDOR" in cond_iva: cond_iva = "Cons. Final"
        self.cell(40, 6, cond_iva, 0)

        # Domicilio (L20, C10)
        self.set_font('Arial', '', 8) 
        
        raw_dom = str(cliente_data.get('domicilio_fiscal', '')).upper().replace('SIN DOMICILIO FISCAL', '')
        if not raw_dom: raw_dom = str(cliente_data.get('domicilio', '')).upper()
        
        dom_lines = textwrap.wrap(raw_dom, 45)[:4] 
        
        last_dom_line_idx = 20
        for i, line_text in enumerate(dom_lines):
            set_bas_xy(20 + i, 10)
            self.cell(80, 5, line_text, 0)
            last_dom_line_idx = 20 + i
            
        # Ref (A facturar, Obs, Valor)
        ref = cliente_data.get('referencia', '')
        if ref:
             set_bas_xy(last_dom_line_idx + 4, 10)
             self.set_font('Arial', '', 6) 
             self.cell(100, 4, f"REF: {ref}", 0)
             
        self.set_font('Arial', 'B', 10) 

        # --- CUERPO (L31) ---
        Y_LIMIT = 58 
        current_line = 31
        
        self.set_font('Courier', '', 10) 
        
        for item in items:
            if current_line > Y_LIMIT: 
                self.add_page()
                current_line = 31
            
            # Cantidad (C4)
            set_bas_xy(current_line, 4)
            self.cell(15, 5, str(item.get('cantidad', '')), 0, 0, 'R')
            
            # Unidad (C16)
            set_bas_xy(current_line, 16)
            self.cell(10, 5, str(item.get('unidad', '')), 0)
            
            # Codigo (C20)
            set_bas_xy(current_line, 20)
            raw_code = str(item.get('codigo', ''))
            # Robust strip: SKU-, SKU , SKU (case insensitive)
            code_clean = raw_code.upper().replace('SKU-', '').replace('SKU ', '').replace('SKU', '').strip()
            self.cell(20, 5, code_clean, 0)
            
            # Descripcion (C28)
            set_bas_xy(current_line, 28)
            self.cell(100, 5, str(item.get('descripcion', '')), 0)
            
            current_line += 1.5

        # --- PIE DE PÁGINA (Observaciones, Valor, Bultos) ---
        # Se imprime siempre en la última página o donde caiga si hay espacio
        # Usamos filas 60+ (aprox 210mm)
        
        # Nota / Observaciones (C62 -> Y=219mm)
        set_bas_xy(60, 4) 
        self.set_font('Arial', 'B', 8)
        self.cell(20, 5, "NOTAS:", 0)
        
        set_bas_xy(60, 10)
        self.set_font('Arial', '', 8)
        obs_text = str(cliente_data.get('observaciones', ''))
        self.multi_cell(140, 4, obs_text, 0)
        
        # Valor Declarado y Bultos (C64 -> Y=226mm)
        set_bas_xy(64, 4)
        self.set_font('Arial', 'B', 8)
        self.cell(25, 5, "VALOR DECL.:", 0)
        
        set_bas_xy(64, 12)
        self.set_font('Arial', '', 8)
        val_text = str(cliente_data.get('valor_declarado', ''))
        self.cell(40, 5, val_text, 0)
        
        set_bas_xy(64, 25)
        self.set_font('Arial', 'B', 8)
        self.cell(20, 5, "BULTOS:", 0)
        
        set_bas_xy(64, 31)
        self.set_font('Arial', '', 8)
        bultos_text = str(cliente_data.get('bultos', ''))
        self.cell(20, 5, bultos_text, 0)

def generar_remito_pdf(cliente_data, items, is_preview=False, output_path="remito_final.pdf", numero_remito=None):
    """
    Genera el PDF con las 3 copias.
    numero_remito: string ej "0005-00000001"
    """
    pdf = PDFRemito()
    pdf.is_preview = is_preview
    if numero_remito:
        pdf.remito_numero = numero_remito
    
    # Definir Copias
    if is_preview:
        copias = [("VISTA PREVIA", "")]
    # Definir Copias
    if is_preview:
        copias = [("VISTA PREVIA", "")]
    else:
        # Usamos 'M' que en ZapfDingbats es una flor/asterisco (✲)
        copias = [
            ("ORIGINAL", "M"),
            ("DUPLICADO", "MM"),
            ("TRIPLICADO", "MMM")
        ]

    for label, symbol in copias:
        pdf.copy_label = label
        pdf.copy_symbol = symbol
        pdf.add_content(cliente_data, items)
        
    pdf.output(output_path)
    return output_path

class TestRemitoEngine(unittest.TestCase):
    def test_generacion_full(self):
        cli = {
            "razon_social": "LABORATORIO DE MEDICINA SOCIEDAD ANONIMA E INDUSTRIAL",
            "cuit": "30-58105030-1",
            "domicilio_fiscal": "TRELLES MANUEL R. 1566, CIUDAD AUTONOMA BUENOS AIRES (1416)",
            "condicion_iva": "RESPONSABLE INSCRIPTO",
            "referencia": "A FACTURAR"
        }
        items = [
            {"codigo": "1000", "descripcion": "TOALLA SUPER CORTA CAJA POR 2.500 U", "cantidad": 1, "unidad": "UN"}
        ]
        
        path_prev = generar_remito_pdf(cli, items, is_preview=True, output_path="test_preview_full.pdf", numero_remito="0005-00000001")
        self.assertTrue(os.path.exists(path_prev))

if __name__ == '__main__':
    unittest.main()
