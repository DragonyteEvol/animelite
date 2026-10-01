"""Empaqueta el motor (animelite-engine) en tareas asincronas para la GUI.

Ninguna llamada de red ocurre en el hilo de la UI: todo se lanza en el
QThreadPool y vuelve por señales.
"""
import re
import unicodedata
from dataclasses import dataclass, field


# ---------------------------------------------------------------- utilidades
def _sin_tildes(texto: str) -> str:
    n = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in n if ord(c) < 128)


def _normalizar(titulo: str) -> str:
    t = _sin_tildes(titulo.lower())
    return re.sub(r"[^a-z0-9 ]", " ", t)


@dataclass
class Grupo:
    titulo: str
    coincidencias: list = field(default_factory=list)

    def sitios(self) -> list:
        return sorted({a.sitio for _s, a in self.coincidencias})


def agrupar(todos) -> list:
    """todos: iterable de (sitio_mod, Anime) -> lista de Grupo."""
    por_norm = {}
    for mod, anime in todos:
        k = _normalizar(anime.titulo)
        por_norm.setdefault(k, Grupo(anime.titulo, []))
        por_norm[k].coincidencias.append((mod, anime))
    grupos = list(por_norm.values())
    grupos.sort(key=lambda g: len(g.coincidencias), reverse=True)
    return grupos


# ------------------------------------------------------------------ pipeline
def _sitios():
    from sitios import SITIOS
    return SITIOS


def buscar(query: str, limite=8.0) -> list:
    """Busca en todas las fuentes en paralelo -> lista de Grupo."""
    from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
    import time

    sitios = _sitios()
    t0 = time.perf_counter()
    ex = ThreadPoolExecutor(max_workers=len(sitios))
    resultados = {}
    try:
        futuros = {ex.submit(s.buscar, query): s for s in sitios}
        pendientes = set(futuros)
        while pendientes:
            resto = limite - (time.perf_counter() - t0)
            if resto <= 0:
                break
            done, pendientes = wait(pendientes, timeout=resto,
                                    return_when=FIRST_COMPLETED)
            for f in done:
                try:
                    resultados[futuros[f]] = f.result()
                except Exception:
                    resultados[futuros[f]] = []
        for f in futuros:
            f.cancel()
    finally:
        ex.shutdown(wait=False)

    todos = []
    for s in sitios:
        for a in resultados.get(s) or []:
            todos.append((s, a))
    return agrupar(todos)


def episodios_por_sitio(grupo: Grupo, limite=8.0) -> list:
    """Para cada coincidencia del grupo, obtiene capitulos en paralelo.

    Devuelve bloques [{sitio, mod, anime, epis, rango}]."""
    from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
    import time

    entradas = [(s, a) for s, a in grupo.coincidencias]
    t0 = time.perf_counter()
    ex = ThreadPoolExecutor(max_workers=len(entradas))
    salida = {}
    try:
        futuros = {ex.submit(s.episodios, a): i
                   for i, (s, a) in enumerate(entradas)}
        pendientes = set(futuros)
        while pendientes:
            resto = limite - (time.perf_counter() - t0)
            if resto <= 0:
                break
            done, pendientes = wait(pendientes, timeout=resto,
                                    return_when=FIRST_COMPLETED)
            for f in done:
                i = futuros[f]
                try:
                    salida[i] = f.result()
                except Exception:
                    salida[i] = []
        for f in futuros:
            f.cancel()
    finally:
        ex.shutdown(wait=False)

    bloques = []
    for i, (s, a) in enumerate(entradas):
        eps = salida.get(i) or []
        if not eps:
            continue
        nums = [e.numero for e in eps]
        bloques.append({
            "sitio": a.sitio,
            "mod": s,
            "anime": a,
            "epis": eps,
            "rango": f"{min(nums)}-{max(nums)}",
        })
    return bloques


def bloque_mayor(bloques: list):
    """Elige el bloque con el rango numerico mas alto, ignorando numeracion
    anomala (peliculas con IDs > 400, remasters)."""
    normales = [b for b in bloques
                if b["epis"] and max(e.numero for e in b["epis"]) <= 400]
    elegibles = normales or bloques
    if not elegibles:
        return None, 0, 0
    b = max(elegibles, key=lambda b: max(e.numero for e in b["epis"]))
    mayor = max(e.numero for e in b["epis"])
    total = len(b["epis"])
    return b, mayor, total


def _episodio_para_cap(bloque, cap):
    ep = next((e for e in bloque["epis"] if e.numero == cap), None)
    if ep is None and isinstance(cap, int) and cap >= 1:
        # Numeracion corrida (p. ej. jkanime usa IDs globales): mapear por
        # posicion si la lista es consecutiva.
        nums = sorted(e.numero for e in bloque["epis"])
        if nums and 0 < cap <= len(nums):
            esperado = nums[0] + (cap - 1)
            if nums == list(range(nums[0], nums[0] + len(nums))):
                ep = next((e for e in bloque["epis"] if e.numero == esperado),
                          None)
    return ep


def streams_del_capitulo(bloques, cap, on_progreso=None) -> list:
    """Resuelve embeds de todos los sitios para `cap` en paralelo."""
    from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
    from resolvers import aplicar
    import time

    if not bloques:
        return []

    def _uno(b):
        ep = _episodio_para_cap(b, cap)
        if not ep:
            return []
        try:
            embeds = []
            for _ in range(2):
                embeds = b["mod"].embeds(ep)
                if embeds:
                    break
        except Exception:
            return []
        if not embeds:
            return []
        try:
            ss, _fallidos = aplicar(embeds)
        except Exception:
            return []
        for s in ss:
            s.host = f"{b['sitio']}/{s.host}"
        return ss

    total = len(bloques)
    ex = ThreadPoolExecutor(max_workers=total)
    streams = []
    try:
        futuros = {ex.submit(_uno, b): b for b in bloques}
        pendientes = set(futuros)
        completados = 0
        t0 = time.perf_counter()
        limite = 10.0
        while pendientes:
            resto = limite - (time.perf_counter() - t0)
            if resto <= 0:
                if streams:
                    break
                resto = 3.0
            done, pendientes = wait(pendientes, timeout=resto,
                                    return_when=FIRST_COMPLETED)
            for f in done:
                try:
                    streams.extend(f.result())
                except Exception:
                    pass
                completados += 1
                if on_progreso:
                    on_progreso(60 * completados / total)
        for f in futuros:
            f.cancel()
    finally:
        ex.shutdown(wait=False)
    return streams


def medir(streams, on_progreso=None) -> list:
    """Mide latencia en paralelo y devuelve los OK ordenados por TTFB."""
    from core import probe

    if not streams:
        return []
    return probe.probar_rapido_lista(streams, ventana=2.5, fallback=3.0)


def candidatos_ok(streams, medidos) -> list:
    """Empareja los streams medidos con su Stream original, dedup por url."""
    por_url = {}
    for s in streams:
        por_url.setdefault(s.url, s)
    out = []
    vistos = set()
    for m in (medidos or []):
        url = m.get("url")
        if not url or url in vistos:
            continue
        vistos.add(url)
        st = por_url.get(url)
        out.append({"host": m.get("host", ""), "url": url,
                    "ttfb_ms": m.get("ttfb_ms"), "mbps": m.get("mbps"),
                    "stream": st})
    return out


def candidatos_todos(streams, medidos) -> list:
    """Todos los servidores: primero los medidos (por TTFB), luego los que la
    sonda no pudo medir (muchos CDN rechazan el probe pero mpv los reproduce)."""
    out = candidatos_ok(streams, medidos)
    ok_urls = {c["url"] for c in out}
    for s in streams:
        if s.url in ok_urls:
            continue
        ok_urls.add(s.url)
        out.append({"host": s.host, "url": s.url, "ttfb_ms": None,
                    "mbps": None, "stream": s})
    return out


def mejor(candidatos) -> dict:
    """Elige el candidato a reproducir: el medido mas rapido o el primero."""
    if not candidatos:
        return None
    medidos = [c for c in candidatos if c.get("ttfb_ms") is not None]
    return (medidos or candidatos)[0]