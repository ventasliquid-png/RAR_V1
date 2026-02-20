# α PROTOCOLO ALFA: INICIO DE SESIÓN

> **PROPÓSITO:** Establecer un entorno seguro y sincronizado antes de cualquier intervención.
> **ACTIVACIÓN:** Al iniciar cada sesión de trabajo.

## FASE 0: EL SEGURO DE VIDA (BACKUP FÍSICO)
**MANDATORIO:** Antes de tocar una sola línea de código.
1.  **Copiar:** `pilot.db` -> `pilot_YYYYMMDD_pre_sesion.db`.
2.  **Verificar:** Que el archivo copiado tenga tamaño > 0.
3.  *Si esto falla, ABORTAR INICIO.*

## FASE 1: SINCRONIZACIÓN DE ADN (GIT)
1.  `git fetch origin`
2.  `git pull`
3.  **Confirmar:** "El código local es idéntico al del repositorio remoto".

## FASE 2: PRUEBA DE HUMO (SMOKE TEST)
**Objetivo:** Verificar que estamos conectados a la base de datos correcta.
1.  **Ejecutar:** `python check_db_integrity.py`
2.  **Análisis de Salida:**
    *   **Si Exit Code es 0:** Proceder a Fase 3 (Declaración de Territorio).
    *   **Si Exit Code es 1:** 🛑 **BLOQUEO TOTAL.** Emitir alerta: *"Comandante, los datos no coinciden o falta estructura de 32 bits. Estamos en la base equivocada o desactualizada. NO se permite iniciar sesión."*

> [!WARNING] ALERTA CRÍTICA DE ESTABILIDAD (2026-02-19)
> El Backend V5 presenta **Errores 500 Persistentes** en endpoints de carga masiva (`/clientes`, `/maestros`, `/productos`) al inicio.
> **Causa Probable:** Circular Import o Fallo en Registro de Modelos (`Vinculo` vs `Cliente`) o `InvalidRequestError` en SQLAlchemy.
> **Estado:** PDF Ingestion funciona (aislado), pero la navegación general está comprometida.
> **Acción Requerida:** Prioridad absoluta al iniciar la próxima sesión. Debuggear `backend/main.py` y orden de importación de modelos.

## FASE 3: DECLARACIÓN DE TERRITORIO
**Gy debe iniciar su primera respuesta con:**
> **ESTOY TRABAJANDO SOBRE EL ARCHIVO [NOMBRE] EN LA RAMA [RAMA]**

---
*Firma: Gy (Antigravity)*
