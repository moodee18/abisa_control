@echo off
title SIIA Abisalud - Panel de Inventario
echo ===================================================
echo   Iniciando Panel de Inventario SIIA Abisalud...
echo ===================================================
echo.

set "PYTHON_EXE=python"
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
    powershell -NoProfile -Command "Get-ChildItem -Path '%~dp0.venv' -Recurse -Include *.pyd,*.dll -ErrorAction SilentlyContinue | Unblock-File" >nul 2>&1
) else if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
)

"%PYTHON_EXE%" "%~dp0main.py" --web
if %errorlevel% neq 0 (
    echo.
    echo ===================================================
    echo  AVISO: Si faltan dependencias en este equipo, ejecute:
    echo    python -m venv .venv
    echo    .venv\Scripts\pip install -r requirements.txt
    echo    .venv\Scripts\playwright install chromium
    echo ===================================================
)
pause