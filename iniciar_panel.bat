@echo off
title SIIA Abisalud - Panel de Inventario
echo ===================================================
echo   Iniciando Panel de Inventario SIIA Abisalud...
echo ===================================================
echo.
"%~dp0.venv\Scripts\python.exe" "%~dp0main.py" --web
pause
 