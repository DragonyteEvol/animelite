"""Traducciones ES/EN."""
from . import config

TEXTOS = {
    "es": {
        "app_titulo": "animelite",
        "buscar_ph": "Buscar anime...",
        "buscar_btn": "Buscar",
        "atajo_buscar": "Enter para buscar",
        "vacio_titulo": "Tu proximo anime empieza aqui",
        "vacio_sub": "Escribe el nombre arriba y pulsa Enter.",
        "siguiendo": "Seguir viendo",
        "sin_resultados": "Sin resultados",
        "sin_resultados_sub": "Prueba con otro nombre o escribe en espanol.",
        "buscando": "Buscando...",
        "cargando_episodios": "Cargando capitulos...",
        "resolviendo": "Resolviendo servidores del cap {cap}...",
        "midiendo": "Midiendo latencia...",
        "capitulos": "Capitulos",
        "sin_capitulos": "No se pudieron obtener los capitulos.",
        "servidores": "Servidores",
        "reproducir": "Reproducir",
        "sin_servidores": "No se obtainieron servidores para este capitulo.",
        "sin_respuesta": "Ningun servidor respondio a tiempo.",
        "latencia": "Latencia",
        "anterior": "Atras",
        "volver": "Volver",
        "mpv_falta": "No se encontro mpv. Instalalo con: winget install "
                     "--id shinchiro.mpv -e",
        "cap_de": "Capitulo {cap}",
        "sin_imagen": "Sin portada",
        "capitulo_visto": "Visto el cap {cap}",
        "buscando_sitios": "Buscando en {n} fuentes...",
        "vistas": "vistas",
        "salir": "Salir",
        "acerca": "animelite - motor de busqueda: animelite-cli",
    },
    "en": {
        "app_titulo": "animelite",
        "buscar_ph": "Search anime...",
        "buscar_btn": "Search",
        "atajo_buscar": "Enter to search",
        "vacio_titulo": "Your next anime starts here",
        "vacio_sub": "Type a title above and press Enter.",
        "siguiendo": "Continue watching",
        "sin_resultados": "No results",
        "sin_resultados_sub": "Try another name or type it in English.",
        "buscando": "Searching...",
        "cargando_episodios": "Loading episodes...",
        "resolviendo": "Resolving servers for ep {cap}...",
        "midiendo": "Measuring latency...",
        "capitulos": "Episodes",
        "sin_capitulos": "Could not load episodes.",
        "servidores": "Servers",
        "reproducir": "Play",
        "sin_servidores": "No servers found for this episode.",
        "sin_respuesta": "No server answered in time.",
        "latencia": "Latency",
        "anterior": "Back",
        "volver": "Back",
        "mpv_falta": "mpv not found. Install it with: winget install "
                     "--id shinchiro.mpv -e",
        "cap_de": "Episode {cap}",
        "sin_imagen": "No poster",
        "capitulo_visto": "Watched ep {cap}",
        "buscando_sitios": "Searching {n} sources...",
        "vistas": "views",
        "salir": "Exit",
        "acerca": "animelite - search engine: animelite-cli",
    },
}

_ACTUAL = "es"


def idioma() -> str:
    return _ACTUAL


def fijar(nuevo: str) -> None:
    global _ACTUAL
    if nuevo in TEXTOS:
        _ACTUAL = nuevo


def cargar() -> None:
    fijar(config.config().get("idioma", "es"))


def tr(clave: str, **kw) -> str:
    texto = TEXTOS.get(_ACTUAL, TEXTOS["es"]).get(clave, clave)
    if kw:
        try:
            return texto.format(**kw)
        except Exception:
            return texto
    return texto