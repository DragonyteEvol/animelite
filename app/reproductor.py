"""Deteccion y lanzamiento de mpv (ventana externa)."""
import os
import shutil
import subprocess
import sys

from . import config

RUTAS = [
    r"C:\Users\Public\Documents\mpv\mpv.exe",
    r"C:\Program Files\mpv\mpv.exe",
    r"C:\Program Files (x86)\mpv\mpv.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\mpv\mpv.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\mpv.exe"),
]

EXTRA_BASE = ["--hwdec=auto", "--cache=yes", "--demuxer-readahead-secs=30",
              "--network-timeout=30"]


def encontrar_mpv() -> str:
    env = os.environ.get("MPV_PATH", "").strip().strip('"')
    if env and env.lower().endswith((".exe", ".com")) and os.path.isfile(env):
        return env
    cfg = config.mpv_path()
    if cfg and os.path.isfile(cfg):
        return cfg
    via_path = shutil.which("mpv")
    if via_path and os.path.isfile(via_path):
        return via_path
    for r in RUTAS:
        if r and os.path.isfile(r):
            return r
    return ""


def _args_extra() -> list:
    raw = os.environ.get("MPV_EXTRA", "").strip()
    if not raw:
        return []
    if raw.startswith('"') and raw.endswith('"') and len(raw) > 1:
        raw = raw[1:-1]
    return raw.split()


def construir_args(url: str, referer: str = "", titulo: str = "") -> list:
    args = [encontrar_mpv(), "--force-window=yes"]
    args += _args_extra()
    if referer:
        args.append(f"--http-header-fields=Referer: {referer}")
    if titulo:
        args.append(f"--title={titulo}")
    args.append(url)
    return args


def reproducir(url: str, referer: str = "", titulo: str = "") -> bool:
    """Lanza mpv en su propia ventana (no bloqueante). True si arranco."""
    mpv = encontrar_mpv()
    if not mpv:
        return False
    args = construir_args(url, referer, titulo)
    if os.name == "nt":
        flags = getattr(subprocess, "DETACHED_PROCESS", 0)
        flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        subprocess.Popen(args, creationflags=flags,
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
    else:
        subprocess.Popen(args, start_new_session=True)
    return True


def abrir_url(url: str) -> None:
    """Abre una URL en el navegador del sistema (paginas de soporte)."""
    if os.name == "nt":
        os.startfile(url)  # noqa: S606
    else:
        subprocess.Popen(["xdg-open", url])


def sin_python_venv() -> bool:
    return sys.prefix == sys.base_prefix