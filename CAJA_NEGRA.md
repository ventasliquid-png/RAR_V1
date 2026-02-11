# 🕋 CAJA NEGRA: RAR V1 (Satélite Fiscal)

> **ESTADO:** OPERATIVO (FASE 2 - PRODUCCIÓN & EMISIÓN)
> **ÚLTIMA ACTUALIZACIÓN:** 2026-02-11
> **GUARDIÁN:** Gy (Antigravity)

## 1. MÓDULOS ACTIVOS

### A. Identidad & Criptografía (`certs/`)
*   **Estado:** ✅ ACTIVADO
*   **Producción:** `certificado.crt` + `privada.key` instalados y validados.
*   **Conexión:** `Conexion_Blindada.py` operando en modo PRODUCCIÓN (WSAA).

### B. Diseño & Maquetación (`remito_engine.py`)
*   **Estado:** 🟢 V2 ESTABLE
*   **Motor:** `fpdf2` con manejo de capas (Watermarks, White-outs).
*   **Estética:** Fuente `ZapfDingbats` para símbolos (Flor/Estrella).
*   **Layout:** Coordenadas BAS calibradas + Pie de página dinámico (Notas/Bultos).

### C. Controlador de Misión (`launch_protocol.py`)
*   **Estado:** 🟢 ACTIVO
*   **Flujo:** Bucle Infinito (Múltiples emisiones).
*   **Features:**
    *   Búsqueda de Clientes (Nombre/CUIT).
    *   Edición de Notas/Valor/Bultos.
    *   Seguridad de Emisión (Confirmación de N°).
    *   Draft System (Recuperación de fallos).

### D. Cantera de Datos (`v5_cantera_oro.db`)
*   **Estado:** 🟢 EVOLUCIONADA (Schema V2)
*   **Mejoras:** Soporte para SKUs, Unidades normalizadas y Referencias de Factura.

## 2. DEUDA TÉCNICA / NEXT STEPS
1.  **Refactorización:** Mover lógica de negocio de `launch_protocol.py` a `rar_core.py` para aligerar el controlador.
2.  **Backup:** Implementar rotación automática de backups de la DB.
3.  **UI:** Evaluar migración a interfaz web (Flask/FastAPI) para fase 3.
