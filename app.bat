@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Falta el entorno .venv. Ejecutar primero instalar.bat.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m app.main %*