# Ω PROTOCOLO OMEGA: CIERRE DE SESIÓN

> **PROPÓSITO:** Asegurar la integridad del satélite RAR antes de la desconexión.
> **ACTIVACIÓN:** Al finalizar tareas críticas.

## FASE 1: DOCUMENTACIÓN (BUROCRACIA DE MEMORIA)
1.  **Bitácora:** Registrar hitos, errores y soluciones en `BITACORA_DEV.md`.
2.  **Caja Negra:** Actualizar estado de módulos en `CAJA_NEGRA.md`.
3.  **Informe Histórico:** Generar `INFORME_SESION_[FECHA].md`.
4.  *Sin informe, no hay cierre.*

## FASE 2: VERIFICACIÓN TÉCNICA
1.  **Consistencia de 32 Bits:** Verificar que las tablas críticas (`clientes`, `productos`, `pedidos`) tengan la columna `flags_estado`.
2.  **El Sello de Órbita:** `git status` limpio. Comparar Hash local vs remoto.

## FASE 3: EL PUNTO DE RESTAURACIÓN (PLAN B)
**MANDATORIO:** Antes del push final.
1.  **Crear Rama de Respaldo:** 
    `git branch backup/YYYYMMDD_HHMM_cierre`
2.  **Objetivo:** Crear una "caja negra" inmutable del estado actual.

## FASE 4: CRIPTOGRAFÍA DE CIERRE
1.  **Git Status:** Revisar cambios pendientes.
2.  **PIN 1974:** El operador HUMANO debe autorizar explícitamente el cierre con el código "1974".
    *   *Sin el PIN, el sistema permanece abierto.*
3.  **Commit Final:** "Protocolo Omega: [Resumen de Misión]".
4.  **Push:** Enviar a remoto.

---
*Firma: Gy (Antigravity)*
