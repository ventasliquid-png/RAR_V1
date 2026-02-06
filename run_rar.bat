@echo off
TITLE RAR - Remitos Arca y Recolector
SET LOCAL_DIR=C:\dev\RAR_V1
cd /d %LOCAL_DIR%

:: Verificar si existe el entorno virtual
if not exist venv (
    echo [*] Creando entorno virtual para RAR...
    python -m venv venv
)

:: Activar entorno
echo [*] Activando Unidad RAR...
call venv\Scripts\activate

:: Verificar librerias (solo si falta pandas)
python -c "import pandas" 2>NUL
if %errorlevel% neq 0 (
    echo [*] Instalando suministros...
    pip install -r requirements.txt --quiet
)

:: Ejecutar el script principal
echo [*] Iniciando Protocolo de Procesamiento...
echo ------------------------------------------
python main.py
echo ------------------------------------------

echo [*] Operacion finalizada.
pause