# 📓 BITÁCORA DE DESARROLLO - RAR V1

## 📅 SESIÓN: 2026-02-10

### 🎯 OBJETIVOS
1.  **Protocolo ALFA:** Activación del Satélite y reconocimiento de identidad (Gy).
2.  **Script 1 (Identidad Fiscal):** Generación de claves criptográficas.
3.  **Script 1 (Diseño):** Creación de la plantilla base para remitos (`base_remito_v1.png`).

### 🛠️ TAREAS REALIZADAS
*   **Protocolo ALFA:**
    *   Se modificó `DESPERTAR_RAR.bat` para incluir identidad de Gy.
    *   Se leyó contexto (`BOOTLOADER`, `DEFINITION`, `PERSONA`).
*   **Criptografía:**
    *   Se generó `certs/produccion_liquid.key` (2048 bits).
    *   Se generó `certs/produccion_liquid.csr` con datos de SONIDO LIQUIDO S.R.L.
*   **Diseño (Iterativo):**
    *   *Intento 1:* Recoloreado simple + Injerto. (Rechazado: Logo tapaba dirección).
    *   *Intento 2:* Limpieza y redibujado de líneas. (Rechazado: Pérdida de calidad/"arratonado").
    *   *Intento 3 (Final):* **Smart Tinting**. Uso de `ImageOps.colorize` global para preservar anti-aliasing + Máscara de Saturación para proteger el logo. (Aprobado).
    *   **Resultado:** `base_remito_v1.png` instituido.

### ⚠️ INCIDENCIAS / BLOQUEOS
*   **Diseño:** La limpieza de ruido y redibujado vectorial (morphological filters) degradó la calidad del texto escaneado. Se optó por un enfoque de tintado cromático (cambio de espectro de color) que preserva la suavidad original del escaneo.
*   **AFIP:** Falta tramitar el Certificado Digital y el Punto de Venta para avanzar a la Fase 2 (Emisión REAL).

### 📝 NOTAS TÉCNICAS
*   El script `advanced_recolor.py` es el canon actual para regenerar la plantilla si cambia el escaneo original.
*   La clave privada NO DEBE compartirse.

## 📅 SESIÓN: 2026-02-11

### 🎯 OBJETIVOS
1.  **Protocolo ALFA:** Asumir control y reportar estado operativo.
2.  **Fase 2 (Producción):** Activar entorno de emisión real confirmando certificado y actualizando módulos críticos.

### 🛠️ TAREAS REALIZADAS
*   **Validación Fiscal (Producción):**
    *   Ejecución de `test_afip_connection.py`.
    *   **Resultado:** El certificado `certificado.crt` (junto con `privada.key`) es válido para **PRODUCCIÓN**.
    *   *Nota:* Se descartó `produccion_liquid.key` por no corresponder al certificado instalado.
*   **Evolución DB (Cantera de Oro):**
    *   `v5_cantera_oro.db` actualizada.
    *   Agregado: Columna `unidad_medida` en `cantera_productos`.
    *   Creado: Tabla `remitos` con columna `referencia_factura`.
*   **Módulo Tomás (Ingesta):**
    *   Implementado `ingesta_bas.py` con lógica de "Consistencia Proactiva".
    *   Probado caso de uso "Guantes" $\rightarrow$ Detección de item nuevo $\rightarrow$ Solicitud de Unidad.
*   **Motor Impresión:**
    *   Reescrito `remito_engine.py` usando `fpdf2` y diseño en capas.
    *   Integrado `base_remito_v1.png`.
    *   Configurado bucle de 3 copias (Original, Duplicado, Triplicado) y Marca de Agua para previews.

### 🚀 FASE 2: DESPLIEGUE (Feedback Loop)
*   **Refinamiento UX/UI:**
    *   **Búsqueda de Clientes:** Implementado motor de búsqueda SQL (`LIKE`) por Razón Social o CUIT.
    *   **Campos Faltantes:** Agregado soporte display/print para `Bultos`, `Valor Declarado` y `Observaciones` (Pie de página).
    *   **Workflow:** Transformado `launch_protocol.py` en bucle infinito para permitir múltiples emisiones sin reinicio.
*   **Estética & Pulido:**
    *   **Limpieza:** Implementación de "White-outs" (Parches blancos) para ocultar elementos obsoletos de la plantilla base.
    *   **Tipografía:** Uso de fuente `ZapfDingbats` (Glifo 'M' = ✲) para indicadores limpia de copias.
*   **Seguridad Operativa:**
    *   **Inputs Blindados:** Reemplazo de comandos de texto por selectores numéricos (`1=SI`, `9=NO`).
    *   **Confirmación de Tiro:** Paso de verificación explícita del N° de Remito antes de la emisión final.
