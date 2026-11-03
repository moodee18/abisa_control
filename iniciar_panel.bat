@echo off
title SIIA Abisalud - Panel de Inventario
echo ===================================================
echo   Iniciando Panel de Inventario SIIA Abisalud...
echo ===================================================
echo.

:: Asegurar que librerias binarias no esten bloqueadas por Windows
powershell -NoProfile -Command "Get-ChildItem -Path '%~dp0.venv' -Recurse -Include *.pyd,*.dll -ErrorAction SilentlyContinue | Unblock-File" >nul 2>&1

"%~dp0.venv\Scripts\python.exe" "%~dp0main.py" --web
if %errorlevel% neq 0 (
    echo.
    echo ===================================================
    echo  AVISO: Si aparece un error de "Control de aplicaciones",
    echo  abra "Seguridad de Windows" ^> "Control de aplicaciones y navegador"
    echo  ^> "Control inteligente de aplicaciones" y pongalo en Desactivado.
    echo ===================================================
)
pause