"""Historial local de 'seguir viendo'."""
import os
import time

from . import config

def _ruta() -> str:
    return os.path.join(os.path.dirname(config.ruta()), "historial.json")


def _leer() -> dict:
    import json
    try:
        with open(_ruta(), "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def _escribir(d: dict) -> None:
    import json
    os.makedirs(os.path.dirname(_ruta()), exist_ok=True)
    with open(_ruta(), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def _clave(anime) -> str:
    return f"{anime.sitio}|{anime.slug}"


def registrar(anime, cap: int) -> None:
    d = _leer()
    d[_clave(anime)] = {
        "titulo": anime.titulo,
        "imagen": anime.imagen,
        "sitio": anime.sitio,
        "slug": anime.slug,
        "url": anime.url,
        "cap": int(cap),
        "ts": time.time(),
    }
    # Recorta a los 40 mas recientes
    ordenados = sorted(d.items(), key=lambda kv: kv[1].get("ts", 0), reverse=True)
    _escribir(dict(ordenados[:40]))


def recientes(limite: int = 8) -> list:
    d = _leer()
    ordenados = sorted(d.items(), key=lambda kv: kv[1].get("ts", 0), reverse=True)
    return [v for _k, v in ordenados[:limite]]


def limpiar() -> None:
    _escribir({})