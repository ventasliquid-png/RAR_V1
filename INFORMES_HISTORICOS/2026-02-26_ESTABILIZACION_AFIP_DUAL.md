# 🦅 INFORME TÉCNICO: ESTABILIZACIÓN IDENTIDAD DUAL AFIP (RAR V1)

**Fecha:** 2026-02-26
**Misión:** Recuperación de Conexión Padrón A13 y Solución de DN Mismatch.
**Estado:** 🟢 OPERATIVO GOLD

## 1. DIAGNÓSTICO DE FALLA
El sistema reportaba un error de `DN del Source invalido` al intentar obtener tickets de acceso (tokens) de la AFIP.

### Hallazgos Forenses:
- **Discrepancia de Identidad:** El código intentaba firmar un pedido para el CUIT de la Empresa (30...) con un certificado que pertenece al CUIT Personal (20...).
- **Criterio Lexicográfico:** AFIP rechazaba el "Common Name" (CN) porque se enviaba en minúsculas (`rar_v5`) cuando el certificado personal lo tiene registrado en mayúsculas (`RAR_V5`).

## 2. INTERVENCIÓN: ARQUITECTURA DUAL
Se refactorizó `Conexion_Blindada.py` para desacoplar las identidades.

*   **Lógica de Conmutación:** El sistema ahora detecta la llave de identidad (`padron` vs `fiscal`) y selecciona el par (Certificado + CUIT + Alias Case-Sensitive) adecuado.
*   **Identidades Configuradas:**
    *   **Padrón (Personal):** CUIT 20132967572 | Cert original feb | Alias `RAR_V5`.
    *   **Fiscal (Empresa):** CUIT 30715603973 | Cert empresa | Alias `rar_v5`.

## 3. PRUEBAS DE INTEGRIDAD
Se superaron los tests de handshake para ambos perfiles:
- [x] **WS_SR_PADRON_A13:** Handshake OK. Consulta exitosa de datos reales.
- [x] **WSMTXCA:** Handshake OK. Token generado exitosamente.

## 4. CIERRE DE SESIÓN
El sistema se deja en estado estable y documentado. El puente con Sonido_Liquido_V5 está verificado y funcional.

---
**Firma:** Agente Antigravity / Gy V14
