import sys
import os
from datetime import datetime
import json
import sqlite3

# Import modules
from Conexion_Blindada import get_datos_afip, solicitar_cae, LOG_PATH
from remito_engine import generar_remito_pdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "v5_cantera_oro.db")
DRAFT_PATH = os.path.join(BASE_DIR, "remito_borrador.json")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def header(text):
    print(f"\n=== {text} ===")

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def auto_generar_proximo_id(cursor, tabla, columna, inicio=1):
    try:
        cursor.execute(f"SELECT MAX({columna}) FROM {tabla}")
        res = cursor.fetchone()
        max_id = res[0] if res and res[0] is not None else None
        
        if max_id is None:
            return inicio
        return max_id + 1
    except Exception as e:
        print(f"Error generando ID para {tabla}.{columna}: {e}")
        return inicio

def save_draft(cliente, items, obs, valor_declarado):
    try:
        draft = {
            "cliente": cliente,
            "items": items,
            "observaciones": obs,
            "valor_declarado": valor_declarado,
            "timestamp": datetime.now().isoformat()
        }
        with open(DRAFT_PATH, 'w', encoding='utf-8') as f:
            json.dump(draft, f, indent=4)
        print("\n[BORRADOR] Estado guardado exitosamente en 'remito_borrador.json'.")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar borrador: {e}")

def load_draft():
    if os.path.exists(DRAFT_PATH):
        try:
            with open(DRAFT_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def buscar_producto(cursor, termino):
    termino = f"%{termino}%"
    cursor.execute("""
        SELECT sku, codigo, descripcion, unidad_medida, precio 
        FROM cantera_productos 
        WHERE descripcion LIKE ? OR codigo LIKE ? OR CAST(sku AS TEXT) LIKE ?
    """, (termino, termino, termino))
    return cursor.fetchall()

def agregar_producto(conn):
    header("BUSCAR / AGREGAR PRODUCTO")
    cursor = conn.cursor()
    
    while True:
        busqueda = input("Buscar (Descripción/Código) o ENTER para Nuevo: ").strip().upper()
        
        if not busqueda:
            # FLUJO NUEVO PRODUCTO
            print("\n--- NUEVO PRODUCTO ---")
            nuevo_sku = auto_generar_proximo_id(cursor, "cantera_productos", "sku", inicio=1000)
            
            # Default Code without SKU prefix if preferred, user said "SKU term shouldn't appear"
            # But the requirement was "visual code". Let's stick to SKU-1000 default but allow override.
            codigo_visual = input(f"Código Visual (Enter = {nuevo_sku}): ").strip().upper()
            if not codigo_visual: codigo_visual = str(nuevo_sku)
            
            desc = input("Descripción: ").strip().upper()
            if not desc: return None
            
            unidad = input("Unidad (UN/KG/M) [UN]: ").strip().upper()
            if not unidad: unidad = "UN"
            if unidad == "U": unidad = "UN" # Normalization
            
            precio_str = input("Precio (Ref): ").strip()
            precio = float(precio_str) if precio_str else 0.0
            
            cantidad = input("Cantidad a Remitir: ").strip()
            
            # Guardar
            cursor.execute("INSERT INTO cantera_productos (sku, codigo, descripcion, unidad_medida, precio) VALUES (?, ?, ?, ?, ?)",
                           (nuevo_sku, codigo_visual, desc, unidad, precio))
            conn.commit()
            print(f"[DB] Producto Creado (SKU {nuevo_sku})")
            
            return {
                "codigo": codigo_visual, 
                "descripcion": desc, 
                "cantidad": cantidad, 
                "unidad": unidad, 
                "sku": nuevo_sku
            }
        
        else:
            # FLUJO BÚSQUEDA
            resultados = buscar_producto(cursor, busqueda)
            if not resultados:
                print("No se encontraron productos. Intente nuevamente o ENTER para crear.")
                continue
                
            print(f"\nResultados para '{busqueda}':")
            for i, prod in enumerate(resultados):
                # prod: (sku, codigo, desc, um, precio)
                print(f"[{i+1}] {prod[2]} (Código: {prod[1]})") # Removed internal SKU display
            
            seleccion = input("\nSeleccione #, (N)uevo, o Enter para buscar otro: ").strip().upper()
            
            if seleccion == 'N':
                # Force new creation logic loop
                busqueda = "" 
                continue

            elif seleccion.isdigit():
                idx = int(seleccion) - 1
                if 0 <= idx < len(resultados):
                    target = resultados[idx]
                    cantidad = input(f"Cantidad para '{target[2]}': ").strip()
                    unidad = target[3]
                    if unidad == "U": unidad = "UN" # Normalization on fetch too just in case

                    return {
                        "codigo": target[1], 
                        "descripcion": target[2], 
                        "cantidad": cantidad, 
                        "unidad": unidad, 
                        "sku": target[0]
                    }
                else:
                    print("Selección inválida.")

def buscar_cliente(cursor, termino):
    termino = f"%{termino}%"
    cursor.execute("""
        SELECT cuit, razon_social, codigo_interno 
        FROM cantera_clientes 
        WHERE razon_social LIKE ? OR cuit LIKE ?
    """, (termino, termino))
    return cursor.fetchall()

def step_cliente(conn):
    header("PASO 1: DATOS DEL CLIENTE Y CABECERA")
    cursor = conn.cursor()
    
    # 1.1 Cliente (Loop de Búsqueda)
    while True:
        entrada = input("Buscar Cliente (Nombre/CUIT) o ENTER para Carga Manual/AFIP: ").strip().upper()
        
        cuit_seleccionado = None
        
        if not entrada:
            # Flujo Manual Original
            c = input("Ingrese CUIT Cliente: ").strip()
            if not c: continue
            cuit_seleccionado = c
        else:
            # Flujo Búsqueda
            resultados = buscar_cliente(cursor, entrada)
            if not resultados:
                print("No se encontraron clientes. Intente nuevamente o ENTER para Carga Manual.")
                continue
                
            print(f"\nResultados para '{entrada}':")
            for i, cli in enumerate(resultados):
                # cli: (cuit, razon_social, codigo_interno)
                code_display = f" [ID: {cli[2]}]" if cli[2] else ""
                print(f"[{i+1}] {cli[1]} (CUIT: {cli[0]}){code_display}")
            
            sel = input("\nSeleccione #, (N)ueva Búsqueda, o Enter para Manual: ").strip().upper()
            
            if sel.isdigit():
                idx = int(sel) - 1
                if 0 <= idx < len(resultados):
                    cuit_seleccionado = resultados[idx][0]
                else:
                    print("Selección inválida.")
                    continue
            elif sel == 'N':
                continue
            else:
                # Manual fallback
                c = input("Ingrese CUIT Cliente: ").strip()
                if not c: continue
                cuit_seleccionado = c

        # Procesar CUIT Seleccionado (Lógica original reutilizada)
        if cuit_seleccionado:
            cursor.execute("SELECT * FROM cantera_clientes WHERE cuit = ?", (cuit_seleccionado,))
            row = cursor.fetchone()
            cols = [d[0] for d in cursor.description]
            
            datos = {}
            if row:
                datos = dict(zip(cols, row))
                print(f"[DB] Cliente Seleccionado: {datos.get('razon_social')}")
                if not datos.get('codigo_interno'):
                    new_id = auto_generar_proximo_id(cursor, "cantera_clientes", "codigo_interno", inicio=1)
                    cursor.execute("UPDATE cantera_clientes SET codigo_interno = ? WHERE cuit = ?", (new_id, cuit_seleccionado))
                    conn.commit()
                    datos['codigo_interno'] = new_id
                break # Cliente encontrado y procesado loop break
            else:
                print(f"[*] Consultando ARCA para {cuit_seleccionado}...")
                datos_afip = get_datos_afip(cuit_seleccionado)
                if "error" in datos_afip:
                    print(f"[ERROR] {datos_afip['error']}")
                    continue
                
                print(f"[OK] {datos_afip['razon_social']}")
                if input("¿Dar de alta en Cantera? (S/N): ").upper() == 'S':
                    new_id = auto_generar_proximo_id(cursor, "cantera_clientes", "codigo_interno", inicio=1)
                    sucursales = json.dumps([{"id": 1, "direccion": datos_afip['domicilio_fiscal'], "alias": "Fiscal"}])
                    cursor.execute("""
                        INSERT INTO cantera_clientes (cuit, razon_social, condicion_iva, domicilio_fiscal, sucursales_json, codigo_interno)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (datos_afip['cuit'], datos_afip['razon_social'], datos_afip['condicion_iva'], datos_afip['domicilio_fiscal'], sucursales, new_id))
                    conn.commit()
                    datos = datos_afip
                    datos['codigo_interno'] = new_id
                    break # Cliente procesado break
                else:
                    continue

    # 1.2 Transacción
    print("\n--- CABECERA REMITO ---")
    while True:
        facturar_opt = input("¿A FACTURAR? (1=SI / 2=NO): ").strip()
        if facturar_opt == '1':
            referencia = "A FACTURAR"
            break
        elif facturar_opt == '2':
            referencia = "NO FACTURAR"
            break
            
    datos['referencia'] = referencia
    
    return datos

def main():
    start_time = datetime.now()
    header(f"SISTEMA DE REMITOS RAR V1 - {start_time.strftime('%H:%M')}")
    
    conn = get_db_connection()
    cursor = conn.cursor()

    while True:
        # MENU INICIAL DE SESIÓN
        print("\n=== INICIO DE OPERACIÓN ===")
        print("1. NUEVO REMITO")
        print("9. SALIR DEL SISTEMA")
        start_op = input("Opción: ").strip()
        
        if start_op == '9':
            print("Cerrando sistema...")
            break
        elif start_op != '1':
            continue

        use_draft = False
        if os.path.exists("remito_borrador.json"):
            draft = load_draft()
            if draft and input("⚠ Se encontró un BORRADOR. ¿Recuperar? (1=SI / 2=NO): ").strip() == '1':
                cliente = draft.get('cliente')
                items = draft.get('items', [])
                obs = draft.get('observaciones', '')
                valor_declarado = draft.get('valor_declarado', '')
                bultos = draft.get('bultos', '')
                use_draft = True
            else:
                if os.path.exists("remito_borrador.json"):
                    os.remove("remito_borrador.json")

        if not use_draft:
            # STEP 1: Cliente & Header
            try:
                cliente = step_cliente(conn)
            except KeyboardInterrupt:
                continue # Allow canceling client selection
                
            items = []
            obs = ""
            valor_declarado = ""
            bultos = ""
            
            # Auto-trigger first product
            clear_screen()
            it = agregar_producto(conn)
            if it: items.append(it)
        
        # STEP 2: Cuerpo Productos (Loop)
        while True:
            clear_screen()
            print(f"CLIENTE: {cliente.get('razon_social', 'Unknown')}")
            print(f"ITEMS: {len(items)}")
            for i, it in enumerate(items):
                print(f"  {i+1}. {it['descripcion']} ({it['cantidad']} {it['unidad']})")
            
            print("\n--- ESTADO ACTUAL ---")
            print(f"Observaciones: {obs if obs else '[Vacío]'}")
            print(f"Valor Decl.  : {valor_declarado if valor_declarado else '[Vacío]'}")
            print(f"Bultos       : {bultos if bultos else '[Vacío]'}")
                
            print("\n--- MENÚ PRINCIPAL ---")
            print("1. AGREGAR Producto")
            print("2. ELIMINAR Último Item")
            print("3. EDITAR Obs / Valor / Bultos")
            print("4. GUARDAR Borrador (Pausa)")
            print("5. FINALIZAR y VER PREVIEW")
            print("9. SALIR (Sin Guardar)")
            
            op = input("Opción: ").strip()
            
            if op == '1':
                it = agregar_producto(conn)
                if it: items.append(it)
            elif op == '2':
                if items: 
                    removed = items.pop()
                    print(f"Eliminado: {removed['descripcion']}")
                    input("Enter para continuar...")
            elif op == '3':
                print(f"\n[EDITAR DATOS ADICIONALES]")
                obs_new = input(f"Observaciones [{obs}]: ").strip()
                if obs_new: obs = obs_new
                
                val_new = input(f"Valor Declarado [{valor_declarado}]: ").strip()
                if val_new: valor_declarado = val_new
                
                bultos_new = input(f"Bultos [{bultos}]: ").strip()
                if bultos_new: bultos = bultos_new
                
            elif op == '4':
                save_draft(cliente, items, obs, valor_declarado)
                print("Borrador guardado.")
                if input("¿Volver al Inicio? (1=SI / 2=NO): ").strip() == '1':
                   break # Goes back to main loop
            elif op == '5':
                if not items:
                    print("¡Error! Debe haber al menos 1 item.")
                    input("Enter para continuar...")
                    continue
                    
                # STEP 3: Preview y Emisión
                full_ref = cliente.get('referencia', '')
                if obs: full_ref += f" | {obs}"
                if valor_declarado: full_ref += f" | Valor: {valor_declarado}"
                
                cliente_preview = cliente.copy()
                cliente_preview['referencia'] = full_ref
                if obs: cliente_preview['observaciones'] = obs
                if valor_declarado: cliente_preview['valor_declarado'] = valor_declarado
                if bultos: cliente_preview['bultos'] = bultos

                # ASK NUMBER BEFORE PREVIEW
                header("DEFINICIÓN DE NÚMERO (PARA PREVIEW)")
                proximo_remito = input("Ingrese Próximo N° Remito (Ej: 1 o 0005-00000001): ").strip()
                if not proximo_remito: 
                    proximo_remito = "0005-00000001"
                elif proximo_remito.isdigit():
                    proximo_remito = f"0005-{int(proximo_remito):08d}"

                header("VISTA PREVIA MODELO")
                print("Generando PDF Preview...")
                pdf_preview = generar_remito_pdf(cliente_preview, items, is_preview=True, output_path="remito_preview.pdf", numero_remito=proximo_remito)
                if os.name == 'nt': os.startfile(pdf_preview)
                
                header("CONFIRMACIÓN DE EMISIÓN")
                print(f"⚠ ESTÁS A PUNTO DE EMITIR EL REMITO N°: {proximo_remito}")
                print(f"   CLIENTE: {cliente['razon_social']}")
                print(f"   ITEMS  : {len(items)}")
                print("\n1. EMITIR DEFINITIVO (Confirmar)")
                print("9. VOLVER AL MENÚ (Corregir)")
                
                emit_op = input("\nOpción: ").strip()
                
                if emit_op == '1':
                    # Check de seguridad
                    seguridad = input(f"CONFIRME N° {proximo_remito} (1=SI / ANY=CANCELAR): ").strip()
                    if seguridad != '1':
                        print("Cancelado.")
                        input("Enter para volver al menú...")
                        continue

                    print("Solicitando CAE a AFIP (Simulado)...")
                    try:
                        cae_data = solicitar_cae({"cuit": cliente['cuit'], "items": items})
                        cliente_preview['referencia'] += f"\nCAE: {cae_data['cae']} Vto: {cae_data['vto_cae']}"
                        
                        pdf_final = generar_remito_pdf(cliente_preview, items, is_preview=False, output_path="remito_final_legal.pdf", numero_remito=proximo_remito)
                        print(f"\n✅ REMITO {proximo_remito} EMITIDO: {pdf_final}")
                        if os.name == 'nt': os.startfile(pdf_final)
                        
                        if os.path.exists("remito_borrador.json"):
                            os.remove("remito_borrador.json")
                        if os.path.exists("remito_preview.pdf"):
                            os.remove("remito_preview.pdf")
                            
                        input("Enter para finalizar y volver al inicio...")
                        break # Breaks inner loop, goes to main loop
                        
                    except Exception as e:
                        print(f"❌ Error al emitir: {e}")
                        save_draft(cliente, items, obs, valor_declarado)
                        print("Se guardó un borrador de emergencia.")
                        input("Enter para continuar...")
                else:
                    continue # Volver al menú
            
            elif op == '9':
                if input("¿Seguro salir sin guardar? (1=SI / 2=NO): ").strip() == '1':
                   break # Breaks inner loop

    conn.close()

if __name__ == "__main__":
    main()
