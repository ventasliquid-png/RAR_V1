# 📡 RAR V1 (REMITOS ARCA & RECOLECTOR) - ARTEFACTO DE IDENTIDAD
> **CLASIFICACIÓN: TOP SECRET // SOLO OJOS GY**
> **PROPÓSITO:** Inyección Cognitiva para Arquitectos AI y Operadores V5.

## 1. Misión Táctica
RAR no es un módulo de V5. Es un **Satélite Autónomo de Inteligencia Fiscal**.
Su función es actuar como **"Esclusa de Verdad"**:
1.  **Ingesta:** Recibe datos sucios (BAS, Excel, Legados).
2.  **Purificación:** Valida contra el Padrón A13 de ARCA (AFIP).
3.  **Cristalización:** Guarda el dato puro en `cantera_arca.db`.
4.  **Emisión:** Genera el Remito PDF oficial (legalmente válido).

**Regla de Oro:** V5 nunca "inventa" un cliente fiscal. V5 lo solicita a la `cantera_arca.db` de RAR.

---

## 2. Los 3 Pilares de Código

### A. EL NÚCLEO (`rar_core.py`)
Es el cerebro de parsing. Implementa la lógica de los **"3 Cajones"** para determinar la Condición de IVA, ya que ARCA devuelve estructuras anidadas complejas.
*   **Cajón 1 (RegimenGeneral):** Busca Impuestos ID 30 (IVA) $\rightarrow$ Responsable Inscripto. ID 32 $\rightarrow$ Exento.
*   **Cajón 2 (Monotributo):** Si existe el nodo, es Monotributista.
*   **Cajón 3 (General/Flattened):** Fallback para leer `razonSocial` si la respuesta viene aplanada.

### B. LA CONEXIÓN (`Conexion_Blindada.py`)
Es el brazo armado.
*   Usa `openssl` (binario) para firmar certificados `.crt`/`.key`.
*   Genera Tickets de Acceso (TRA/LoginCms).
*   Se conecta al WebService `personaServiceA13`.
*   **Módulo clave:** `get_datos_afip(cuit)` devuelve un dict normalizado o error.

### C. LA CANTERA (`cantera_arca.db`)
La "Single Source of Truth" (SSoT). SQLite 3.
*   `cantera_clientes`:
    *   `cuit` (PK)
    *   `razon_social` (Oficial ARCA)
    *   `condicion_iva`
    *   `domicilio_fiscal`
    *   `sucursales_json` (Array de direcciones de entrega extraídas o agregadas).
*   `mapeo_legacy`: Vincula `id_bas` (Sistema Viejo) $\rightarrow$ `cuit`.
*   `cantera_productos`: Catálogo normalizado para impresión de remitos.

---

## 3. Flujo de Operación (The Pipeline)
1.  **Input:** Archivo `REPORTE 2.TXT` (csv sucio del sistema viejo).
2.  **Controller (`main.py`):**
    *   Lee el reporte.
    *   Detecta Clientes Nuevos.
    *   **Si falta:** Pide CUIT al operador $\rightarrow$ Llama a AFIP $\rightarrow$ Guarda en DB.
    *   **Si está:** Usa datos cacheados.
3.  **Output (Futuro Inmediato):** Generación de PDF Remito con la data de `cantera_arca.db`.

---

## 4. Instrucciones para el Arquitecto (Gy / User)
Al retomar RAR, recuerda:
*   **No integrar a la fuerza en V5:** RAR debe madurar como herramienta de validación independiente.
*   **El PDF es la meta:** Tomy necesita el papel/PDF para que el camión salga. La UX es secundaria, la validez fiscal es primaria.
*   **Pathing:** RAR usa rutas absolutas calculadas (`os.path.dirname`) para ser portable. No romper esto.

**Identidad Visual:** `base_remito_v1.png` instituida (Smart Tinting v1.0, White-out V2).
**Firma Digital:** `certs/` preparado para tramitación.
**Motor de Emisión:** `remito_engine.py` V2 (ZapfDingbats, Capas, Pie Dinámico).

*Gy V14 "Vanguard" - 2026-02-11*

## 5. Vision Board: RAR Fase 2 (DESPLEGADA)
> **STATUS:** OPERATIVO (PRODUCCIÓN)
> **STRATEGY:** "Bucle Infinito"

1.  **Carga Unificada:** `launch_protocol.py` orquesta la carga de Clientes, Items y Datos Fiscales.
2.  **Output Bifurcado:**
    *   **Botón A (Remito):** Genera PDF con Cantidades (Original, Dup, Trip). Oculta Precios.
    *   **Botón B (Factura):** Pendiente de linkear con WSFEv1.

