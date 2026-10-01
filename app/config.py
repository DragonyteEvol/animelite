"""Config de la app (compartida con el CLI en %APPDATA%\\animelite)."""
import json
import os

_RUTA = os.path.join(
    os.environ.get("APPDATA") or os.path.expanduser("~"),
    "animelite",
    "config.json",
)


def ruta() -> str:
    return _RUTA


def leer() -> dict:
    try:
        with open(_RUTA, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return datos if isinstance(datos, dict) else {}
    except Exception:
        return {}


def guardar(valores: dict) -> None:
    datos = leer()
    datos.update(valores)
    os.makedirs(os.path.dirname(_RUTA), exist_ok=True)
    with open(_RUTA, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def config() -> dict:
    d = leer()
    d.setdefault("tema", "oscuro")
    d.setdefault("idioma", "es")
    return d


def mpv_path() -> str:
    return leer().get("mpv_path") or ""