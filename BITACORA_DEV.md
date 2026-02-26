
### FECHA: 12/02/2026 - SESIÓN DE IMPLEMENTACIÓN WSMTXCA (FASE 2)

**ESTADO ACTUAL:** 🛑 BLOQUEADO (ADMINISTRATIVO - NO TÉCNICO)

**ACTIVIDADES REALIZADAS:**
1.  **Diagnóstico de Identidad:** Se detectó que el usuario operaba bajo CUIT PERSONAL (20...) en lugar de CUIT EMPRESA (30...). Esto causaba errores de permisos y falta de opciones en AFIP.
2.  **Corrección de Contexto:** Se redirigió la operación al CUIT DE LA EMPRESA "SONIDO LIQUIDO SRL".
3.  **Configuración de Puntos de Venta (PV):**
    *   Se intentó crear PV con sistema "Remito Electrónico Web Services" (PV 7). Resultado: Error 1500 (Rechazo WSMTXCA).
    *   Se intentó crear PV con sistema "RECE para aplicativo y web services" (PV 9). Resultado: Error 1500.
    *   **DIAGNOSTICO:** El sistema WSMTXCA requiere un PV específico ("Codificación de Productos").
4.  **Investigación de Regímenes:**
    *   Se identificó que falta el empadronamiento en "Factura Electrónica con Detalle" dentro del servicio "Regímenes de Facturación y Registración (REAR/RECE/RFI)".
5.  **BLOQUEO FINAL:**
    *   Al intentar el empadronamiento REAR, AFIP bloqueó el trámite por "Falta de presentación de DDJJ Ganancias 202---

### FECHA: 20/02/2026 - SESIÓN DE ESTABILIZACIÓN CRÍTICA Y PUENTE MULTI-IDENTIDAD

**ESTADO ACTUAL:** 🟢 OPERATIVO GOLD

**EVENTO:** Rescate de Backend post-caída sistémica y restauración de comunicación fiscal.

**ACTIVIDADES REALIZADAS:**
1.  **Recuperación ORM:** Se identificó que modelos clave (`contactos`, `remitos`) no estaban registrados en el registry de SQLAlchemy en `main.py`, causando errores 500 al resolver relaciones de `Cliente`. Se aplicó registro explícito.
2.  **Ajuste de Integridad:** El umbral de `check_db_integrity.py` se movió a **33 registros** para reflejar la realidad de la base saneada.
3.  **Puente Multi-Identidad (Hito):**
    *   Se diagnosticó que el permiso de Padrón A13 reside en el CUIT 20132967572, mientras que MTXCA reside en el CUIT 30715603973.
    *   Se refactorizó `Conexion_Blindada.py` para alternar certificados dinámicamente según el servicio solicitado.
4.  **UX Vanguard:** Implementación del **Comparison Overlay** para validación AFIP visual, evitando sobreescrituras accidentales.
5.  **Fix Persistencia:** Se habilitó el mapeo y guardado de domicilios fiscales para clientes existentes (Caso Biotenk), corrigiendo el bypass de actualización en el frontend.

**ERRORES TÉCNICOS RESUELTOS:**
*   `NameError` en `clientes/router.py` (VinculoComercialUpdate).
*   `ImportError: zeep` en entorno virtual del bridge.
*   `Computador No Autorizado` (Resuelto vía Multi-Identity).

**PRÓXIMOS PASOS:**
1.  Finalizar Protocolo Omega.
2.  Delegar Padrón A13 al CUIT 30 para simplificar infraestructura futura.

**ERRORES TÉCNICOS RESUELTOS:**
*   `debug_mtxca.py`: Implementado escáner de PVs, confirmó rechazos en PVs 7 y 9.
*   `remito_arca_engine.py`: Motor PDF v2 listo, validado con datos dummy.
*   **Certificados Digitales:** Validados y funcionando correctamente para `wsmtxca` en producción.

**TAREAS PENDIENTES (POST-DESBLOQUEO):**
1.  Regularizar situación impositiva (Contador).
2.  Empadronar en REAR ("Factura con Detalle").
3.  Crear PV "Codificación de Productos".
4.  Ejecutar emisión de prueba con `Conexion_Blindada.py`.

---

### FECHA: 19/02/2026 - SESIÓN DE RECUPERACIÓN V5 Y REMITO MANUAL

**ESTADO ACTUAL:** 🟢 OPERATIVO (Backend Restaurado)

**INCIDENTE:** Colapso del Backend V5 (Error 500) por inconsistencia de Base de Datos (`pilot.db` vs `pilot_v5x.db`).

**ACCIONES CORRECTIVAS:**
1.  **Diagnóstico:** Se identificó que el entorno cargaba `pilot.db` (obsoleta) ignorando configuración.
2.  **Opción Nuclear:** Se reemplazó `pilot.db` por la versión saneada `pilot_v5x.db` (Schema V7). Problema resuelto de raíz.
3.  **Remito de Contingencia:** Se generó PDF manual para "LAVIMAR" extrayendo datos de factura y sorteando bug de librerías gráficas (`PNG` -> `JPG`).

**LECCIONES APRENDIDAS:**
*   **Persistencia de Entorno:** Los procesos "zombies" de Python pueden mantener conexiones a bases viejas. `taskkill` es mandatorio antes de asumir cambios de config.
*   **Estrategia Git:** Se debe implementar una **RAMA DE RESPALDO** automática al iniciar Protocolo Omega para proteger la integridad de los datos durante refactorizaciones agresivas.

**PRÓXIMOS PASOS:**
1.  Implementar `PDF Parsing` automático (Ingesta de Facturas).
2.  Formalizar la estrategia de Ramas de Respaldo en `PROTOCOLO_OMEGA.md`.

### FECHA: 26/02/2026 - ESTABILIZACIÓN IDENTIDAD DUAL
**ESTADO ACTUAL:** 🟢 OPERATIVO GOLD
**ACTIVIDADES REALIZADAS:**
1.  **Refactor de Identidad:** Implementada arquitectura de conmutación (Personal/Empresa) en `Conexion_Blindada.py`.
2.  **Fix Case-Sensitivity:** Ajustado alias del certificado personal a `RAR_V5` para satisfacer validación estricta de AFIP.
3.  **Verificación:** Handshakes exitosos para Padrón (CUIT 20...) y Fiscal (CUIT 30...).

