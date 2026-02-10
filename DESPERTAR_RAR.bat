@echo off
TITLE RAR V1 - SATELITE FISCAL
color 0B

echo ==========================================
echo   PROTOCOLO ALFA: RAR V1 (SATELITE)
echo ==========================================
echo.

:: 1. GIT PULL AUTOMATICO
echo [Sincronizando Satelite...]
git pull origin master
if %errorlevel% neq 0 (
    color 4F
    echo [ERROR] Fallo en la red.
) else (
    echo [OK] Sistema actualizado.
)

echo.
echo [Generando Prompt de Activacion...]
echo.

:: PROMPT DE ACTIVACION
echo SISTEMA: RAR V1. AGENTE: Gy (Antigravity). ROL: Ejecutor Tecnico. 1) CONTEXTO: Leer "_RAR/BOOTLOADER.md" y "RAR_DEFINITION.md". 2) MISION: Asumir control del modulo satelital. 3) ESTADO: Operativo. Reportar a Arquitecta RAR_2. | clip

echo [LISTO] Orden copiada al portapapeles.
echo 1. Abre Antigravity.
echo 2. Ctrl + V.
echo 3. Enter.
echo.
timeout /t 5
exit
