"""Instalador para la app de escritorio animelite."""
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(REPO, ".venv")
PY_VENV = os.path.join(VENV, "Scripts", "python.exe")
PIP_VENV = os.path.join(VENV, "Scripts", "pip.exe")


def _info(msg):
    print("  [..]", msg)


def _ok(msg):
    print("  [OK]", msg)


def _err(msg):
    print("  [XX]", msg)


def _python_ok():
    r = subprocess.run([sys.executable, "--version"],
                       capture_output=True, text=True)
    linea = (r.stdout or r.stderr).strip()
    _info(f"Python detectado: {linea}")
    try:
        num = linea.split(" ")[-1].split(".")
        return int(num[0]) >= 3 and int(num[1]) >= 10
    except Exception:
        return False


def _crear_venv():
    if os.path.isfile(PY_VENV):
        _ok(".venv ya existia")
        return True
    r = subprocess.run([sys.executable, "-m", "venv", VENV])
    if r.returncode != 0:
        _err("Fallo al crear .venv")
        return False
    _ok(".venv creado")
    return True


def _instalar_deps():
    req = os.path.join(REPO, "requirements.txt")
    r = subprocess.run([PIP_VENV, "install", "-r", req])
    if r.returncode != 0:
        _err("Fallo al instalar dependencias")
        return False
    _ok("dependencias instaladas")
    return True


def main():
    print("=" * 56)
    print("  instalador de animelite (GUI)")
    print("=" * 56)
    if not _python_ok():
        _err("Se necesita Python 3.10 o superior")
        return 1
    if not _crear_venv():
        return 1
    if not _instalar_deps():
        return 1
    print("\n  Listo. Ejecutar: app.bat")
    return 0


if __name__ == "__main__":
    sys.exit(main())