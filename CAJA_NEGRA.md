# 🕋 CAJA NEGRA: RAR V1 (Satélite Fiscal)

> **ESTADO:** OPERATIVO (FASE 1 - DISEÑO & IDENTIDAD)
> **ÚLTIMA ACTUALIZACIÓN:** 2026-02-10
> **GUARDIÁN:** Gy (Antigravity)

## 1. MÓDULOS ACTIVOS

### A. Identidad & Criptografía (`certs/`)
*   **Estado:** ✅ GENERADO
*   **Archivos:** `privada.key` (RSA 2048), `pedido.csr`.
*   **Pendiente:** Obtener `certificado.crt` de AFIP via Clave Fiscal.

### B. Diseño & Maquetación (`base_remito_v1.png`)
*   **Estado:** ✅ INSTITUIDO
*   **Versión:** V1.0 (Smart Tinting + Logo Protegido).
*   **Specs:**
    *   Fondo: Blanco.
    *   Líneas/Texto: Azul Corporativo (`#252b75`).
    *   Logo: "Liquid Sound" Original (Color) en esq. superior izquierda.
    *   Proceso: `advanced_recolor.py` (Colorize + Masking).

### C. Motor de Conexión (`Conexion_Blindada.py`)
*   **Estado:** ⚠️ PARCIAL
*   **Funcional:** Consulta Padrón A13 (`ws_sr_padron_a13`).
*   **Faltante:** Emisión de Comprobantes (`wsfev1` / Remitos). Requiere PV y CRT.

### D. Core Lógico (`rar_core.py`)
*   **Estado:** 🟢 ESTABLE
*   **Función:** Parsing de respuestas A13 (Cajones 1, 2, 3).

## 2. DEUDA TÉCNICA / NEXT STEPS
1.  **Tramitar CRT** en AFIP con el CSR generado.
2.  **Crear Punto de Venta** "Web Service" en AFIP.
3.  **Actualizar `Conexion_Blindada.py`** para soportar `wsfev1` (Factura/Remito).
4.  **Implementar Timbrado:** Estampar CAE y Vencimiento en `base_remito_v1.png`.
