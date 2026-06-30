@echo off
chcp 65001 >nul
title Sistema de Prediccion de Desercion - App Web

echo ============================================================
echo   SISTEMA DE PREDICCION DE DESERCION
echo   App Web Móvil
echo ============================================================
echo.

echo Iniciando servidor...
start "Servidor" cmd /c "python app.py"

echo Esperando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo   SERVIDOR INICIADO
echo ============================================================
echo.
echo   Abre en tu navegador:
echo   http://localhost:8000
echo.
echo   Para detener el servidor, cierra la ventana negra
echo ============================================================
echo.

start http://localhost:8000

pause