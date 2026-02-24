# Ω PROTOCOLO OMEGA: CIERRE DE SESIÓN (RAR V1)

> **PROPÓSITO:** Asegurar la integridad del satélite RAR antes de la desconexión y alinear con la Doctrina GY V5.
> **ACTIVACIÓN:** Al finalizar tareas críticas o cerrar sesión del día.

## 🛑 REGLA CERO: EL FRENO DE MANO (PIN 1974)
Si el Usuario indica "Presentar plan SIN ejecutar" o se invoca el cierre de sesión, **NINGUNA** configuración de auto-aprobación tiene validez.
*   **Acción:** Debes pausar y solicitar confirmación mediante el **PIN Maestro: "1974"**.
*   **CLÁUSULA DE HIERRO:** Comandos como "LGTM" o "Proceed" **NO SUSTITUYEN** al PIN 1974 cuando este protocolo es dictado.

## FASE 1: LA BUROCRACIA (DOCUMENTACIÓN DE MEMORIA)
1.  **Bitácora:** Registrar hitos, errores y soluciones en `BITACORA_DEV.md`.
2.  **Caja Negra:** Actualizar estado de módulos en `CAJA_NEGRA.md` si hubo fallos sistémicos.
3.  **Informe Histórico:** Generar Markdown detallado en la carpeta `INFORMES_HISTORICOS/` narrando intervenciones técnicas (Python/SQLite) o resultados de ingesta. *Sin informe, no hay cierre.*

## FASE 2: VERIFICACIÓN TÉCNICA Y PLANIFICACIÓN
1.  **Consistencia Estructural:** Si se crearon/modificaron tablas, verificar coherencia (Ej: campos `flags_estado`, compatibilidad V5).
2.  **Generar Plan de Implementación (`implementation_plan.md`):** Escribir los pasos exactos para git. Presentarlo al usuario ANTES de continuar.
3.  **STOP:** Presentar reporte de burocracia + plan y esperar el **PIN Maestro "1974"**.

## FASE 3: EJECUCIÓN TÉCNICA (GIT FLOW)
Solo tras recibir la confirmación explícita (**1974**):
1.  **Git Status:** Revisar cambios pendientes. No subir archivos temporales (`.xml`, `.cms`).
2.  **Git Add:** `. `
3.  **Git Commit:** "Protocolo Omega RAR: [Resumen de Misión]".
4.  **Git Push:** Enviar a remoto.

## FASE 3.5: VERIFICACIÓN DE ÓRBITA (TRUST BUT VERIFY)
OBLIGATORIO: Tras el push, NO dar por sentado el éxito.
1.  **Ejecutar:** `git log origin/[RAMA_ACTIVA] -n 1 --format="%h - %s"`
2.  **Validar:** El hash devuelto DEBE coincidir con el hash local.
3.  *Si no coinciden:* Reportar de inmediato "FALLO DE SINCRONIZACIÓN".

---
*Firma: Gy (Antigravity)*
