@echo off
title Instalador de Dependencias - SIIA Abisalud
echo ===================================================
echo   Instalando dependencias de SIIA Abisalud...
echo ===================================================
echo.

if not exist "%~dp0.venv" (
    echo [1/3] Creando entorno virtual .venv...
    python -m venv "%~dp0.venv"
)

echo [2/3] Instalando librerias desde requirements.txt...
"%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip
"%~dp0.venv\Scripts\pip.exe" install -r "%~dp0requirements.txt"

echo.
echo [3/3] Descargando navegador Chromium para el motor RPA...
"%~dp0.venv\Scripts\playwright.exe" install chromium

echo.
echo ===================================================
echo   Instalacion completada con exito!
echo   Ya puedes iniciar el sistema con: iniciar_panel.bat
echo ===================================================
echo.
pause
