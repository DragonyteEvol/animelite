@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [!] Falta el entorno .venv. Ejecuta instalar.bat primero.
  pause
  exit /b 1
)

echo [*] Construyendo EXE con PyInstaller...
".venv\Scripts\python.exe" -m pip install --quiet pyinstaller

".venv\Scripts\pyinstaller.exe" ^
  --name animelite ^
  --onefile ^
  --windowed ^
  --noconsole ^
  --paths . ^
  --collect-submodules resolvers ^
  --collect-submodules sitios ^
  --collect-submodules core ^
  --clean ^
  run.py

if errorlevel 1 (
  echo [!] Error al compilar con PyInstaller.
  pause
  exit /b 1
)

echo [*] Build completado en dist\animelite.exe
echo [*] Carpeta intermedia: build\
pause