# α PROTOCOLO ALFA: INICIO DE SESIÓN (RAR V1)

> **PROPÓSITO:** Establecer un entorno seguro y sincronizado antes de cualquier intervención técnica.
> **ACTIVACIÓN:** Al iniciar cada sesión de trabajo (vía DESPERTAR_AMBOS o DESPERTAR_RAR).

## 🛑 REGLA CERO: IDENTIDAD Y MANDO
1.  **Dualidad:** Si el arranque fue compartido (V5 + RAR), priorizar instrucciones de la Arquitecta General. Si fue local, atender a RAR_2.
2.  **Reporte Obligatorio:** Gy debe iniciar su primera respuesta indicando su posición exacta:
    > **ESTOY TRABAJANDO SOBRE EL ARCHIVO [NOMBRE] EN LA RAMA [RAMA]**

## FASE 0: EL SEGURO DE VIDA (BACKUP FÍSICO)
**MANDATORIO:** Antes de tocar una sola línea de código o procesar un solo dato.
1.  **Copiar:** `cantera_arca.db` -> `cantera_arca_YYYYMMDD_pre_sesion.db`. (Asegurar que sea copia, no mover).
2.  **Verificar:** Que el archivo copiado tenga tamaño > 0.
3.  *Si esto falla, ABORTAR INICIO. Informar al usuario.*

## FASE 1: SINCRONIZACIÓN DE ADN (GIT)
1.  **Ejecutar:** `git fetch origin` && `git pull origin [RAMA_ACTIVA]`
2.  **Confirmar:** "El código local es idéntico al del repositorio remoto".
3.  *Si hay conflictos:* Detener y solicitar intervención manual.

## FASE 2: PRUEBA DE HUMO (SMOKE TEST SATELITAL)
**Objetivo:** Verificar integridad de los conductos hacia V5 y el exterior.
1.  **Ejecutar:** `python check_db.py` (Script de listado/verificación de bases de V1).
2.  **Análisis de Salida:**
    *   **Si Exit Code es 0:** Proceder a Fase 3 (Lectura de Doctrina).
    *   **Si Exit Code es 1:** 🛑 **BLOQUEO TOTAL.** Emitir alerta: *"Comandante, la cantera no responde o los registros están corruptos. NO se permite iniciar operación."*

## FASE 3: LECTURA DE DOCTRINA
1.  Leer obligatoriamente los últimos 2 registros en `INFORMES_HISTORICOS/` para absorber el contexto operativo.
2.  Revisar `_RAR/BOOTLOADER.md` para misiones específicas del día.

---
*Firma: Gy (Antigravity)*
