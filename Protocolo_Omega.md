# Ω PROTOCOLO OMEGA: CIERRE DE SESIÓN

> **PROPÓSITO:** Asegurar la integridad del satélite RAR antes de la desconexión.
> **ACTIVACIÓN:** Al finalizar tareas críticas.

## FASE 1: DOCUMENTACIÓN
1.  **Bitácora:** Registrar hitos, errores y soluciones en `BITACORA_DEV.md`.
2.  **Caja Negra:** Actualizar estado de módulos en `CAJA_NEGRA.md`.
3.  **Manuales:** Reflejar cambios de arquitectura en `RAR_DEFINITION.md`.

## FASE 2: LIMPIEZA
1.  Eliminar archivos temporales de prueba (ej: `*_PRUEBA.png`, `temp_auth.xml`).
2.  Verificar que no queden claves privadas expuestas fuera de `certs/`.

## FASE 3: CRIPTOGRAFÍA DE CIERRE
1.  **Git Status:** Revisar cambios pendientes.
2.  **PIN 1974:** El operador HUMANO debe autorizar el push con el código "1974".
3.  **Commit:** "Protocolo Omega: [Resumen de Misión]".
4.  **Push:** Enviar a remoto.

---
*Firma: Gy (Antigravity)*
