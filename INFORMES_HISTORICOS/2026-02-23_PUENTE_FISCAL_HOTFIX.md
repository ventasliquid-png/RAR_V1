# INFORME HISTÓRICO: HOTFIX PUENTE AFIP (SECRETO FISCAL)

**Fecha:** 23-Feb-2026
**Módulo:** Satélite RAR V1 (`rar_core.py`)
**Operación:** "Sabueso Soberano" (Soporte)
**Nave Principal:** Sonido Liquido V5 (FastAPI)

## 1. El Incidente: La Niebla Fiscal
Durante la ingesta automática de facturas PDF en el sistema V5 y su posterior alta de cliente automatizada, se detectó un fallo sistémico en la ruta de validación AFIP (API `getPersona`). 

El puente estallaba aleatoriamente con un Error 500 originado en el satélite RAR V1, devolviendo un `NoneType object has no attribute 'upper'` proveniente de `rar_core.py`.

## 2. Diagnóstico: El Silencio del Padrón
Al someter consultas hacia CUITs que empezaban con `20`, `23`, `24` o `27` (Personas Físicas / Humanas), se evidenció que la AFIP oculta por ley de Secreto Fiscal sus posiciones impositivas. 

A diferencia de las empresas (`30-*`), la AFIP omite por completo la llave `formaJuridica` y el bloque `datosRegimenGeneral`. El algoritmo V12 asumía la existencia de la variable `formaJuridica` invocando el método `.upper()` para inferir la Sociedad, lo cual detonaba el Crash cuando el JSON devolvía `null`.

## 3. Resolución Técnica
Se le aplicó un "parche de blindaje nulo" dentro de `rar_core.py`:
```python
forma_juridica = (datos.get('formaJuridica') or '').upper()
```
*   **Fallback Seguro:** Si la key no existe o es `None`, se fuerza su lectura como string vacío antes de la capitalización, previniendo el Type Error.
*   **Degradación Selectiva:** Al no tener información explícita de `datosRegimenGeneral`, la heurística de RAR degradará lógicamente al individuo hacia "Consumidor Final" de manera silenciosa, permitiendo que la respuesta viaje intacta de regreso a la Nave Principal (V5).

*(Nota: En V5 se instrumentó paralelamente una "Doctrina de Preservación" para ignorar esta degradación falsa si V5 ya conoce el IVA real).*
