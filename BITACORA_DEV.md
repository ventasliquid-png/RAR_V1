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
