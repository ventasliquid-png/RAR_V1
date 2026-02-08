from flask import Flask, render_template, request, send_file, jsonify
import os
import glob
import json
import traceback

# Importamos módulos RAR
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import inicializar_cantera, procesar_reporte, DB_NAME
from remito_engine import generar_remito_pdf
import sqlite3

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "REPORTE 2.TXT")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_report():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    # Guardamos como REPORTE 2.TXT sobreescribiendo
    file.save(REPORT_PATH)
    
    # Disparamos el procesamiento (Harvest)
    try:
        # Nota: procesar_reporte en main.py está hecho para correr CLI
        # Para la web, necesitamos algo que NO pida input() bloqueante
        # Por ahora, asumimos que main.py usa datos cacheados o falla si no valida.
        # Idealmente refactorizariamos main.py para分離 la lógica de "pedir input".
        # HACK TÁCTICO: Ejecutamos solo si ya existe en DB.
        
        # Leemos el reporte nosotros mismos para mostrar previsualización
        items_preview = []
        with open(REPORT_PATH, 'r', encoding='latin-1') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) >= 9:
                    # Formato BAS: "x","x","ID","RAZON",...,"COD","DESC"
                    items_preview.append({
                        "id_cliente": parts[2].replace('"', ''),
                        "cliente": parts[3].replace('"', ''),
                        "codigo": parts[7].replace('"', ''),
                        "descripcion": parts[8].replace('"', ''),
                        "cantidad": 1 # Default a 1 por ahora, BAS no manda cantidad en REPORTE 2?
                    })
        
        return jsonify({"status": "ok", "items": items_preview})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    cliente_bas_id = data.get('id_cliente')
    items = data.get('items')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Resolver Cliente (BAS -> CUIT -> Datos ARCA)
    # Buscamos en mapeo legacy
    res = cursor.execute("SELECT cuit_referencia FROM mapeo_legacy WHERE id_bas = ?", (cliente_bas_id,)).fetchone()
    if not res:
        conn.close()
        return jsonify({"error": f"Cliente {cliente_bas_id} no mapeado. Ejecute main.py manualmente primero."})
    
    cuit = res[0]
    cli_data = cursor.execute("SELECT * FROM cantera_clientes WHERE cuit = ?", (cuit,)).fetchone()
    conn.close()
    
    if not cli_data:
        return jsonify({"error": "Error de integridad: Mapeo existe pero cliente no."})
        
    cliente_dict = {
        "cuit": cli_data[0],
        "razon_social": cli_data[1],
        "condicion_iva": cli_data[2],
        "domicilio": cli_data[3]
    }
    
    # 2. Generar PDF
    output_filename = f"Remito_{cliente_bas_id}.pdf"
    output_path = os.path.join(BASE_DIR, "static", output_filename)
    if not os.path.exists(os.path.join(BASE_DIR, "static")):
        os.makedirs(os.path.join(BASE_DIR, "static"))
        
    pdf_path = generar_remito_pdf(cliente_dict, items, output_path)
    
    return jsonify({"pdf_url": f"/static/{output_filename}"})

if __name__ == '__main__':
    inicializar_cantera()
    app.run(debug=True, port=5000)
