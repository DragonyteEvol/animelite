"""Autodiagnostico sin interfaz: comprueba el motor dentro del ejecutable.

Uso:
    animelite.exe --selftest [titulo]
    python run.py --selftest frieren

Escribe un informe en %LOCALAPPDATA%\\animelite\\selftest.log y devuelve
0 si el flujo completo funciona (no hace falta que mpv este instalado).
"""
import os
import sys
import time
import traceback


def _log_path() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, "animelite")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "selftest.log")


class _Bitacora:
    def __init__(self, ruta):
        self.ruta = ruta
        self.lineas = []

    def __call__(self, texto=""):
        self.lineas.append(texto)

    def volcar(self):
        cabecera = [f"animelite selftest  {time.strftime('%Y-%m-%d %H:%M:%S')}",
                    "=" * 56]
        cuerpo = cabecera + list(self.lineas)
        try:
            with open(self.ruta, "w", encoding="utf-8") as f:
                f.write("\n".join(cuerpo) + "\n")
        except Exception:
            pass
        return "\n".join(cuerpo)


def _info_python(log):
    log(f"python      : {sys.version.split()[0]}")
    log(f"congelado   : {getattr(sys, 'frozen', False)}")
    log(f"ejecutable  : {sys.executable}")


def _info_motor(log):
    try:
        from sitios import SITIOS
        log(f"fuentes     : {', '.join(s.__name__.rsplit('.', 1)[-1] for s in SITIOS)}")
    except Exception as e:
        raise RuntimeError(f"no se pudo importar 'sitios': {e}")
    try:
        import resolvers
        n = len([n for n in dir(resolvers) if not n.startswith("_")])
        log(f"resolvers   : {n} simbolos publicos")
    except Exception as e:
        raise RuntimeError(f"no se pudo importar 'resolvers': {e}")
    try:
        import core
        log(f"core        : {len([n for n in dir(core) if not n.startswith('_')])} simbolos")
    except Exception as e:
        raise RuntimeError(f"no se pudo importar 'core': {e}")


def _info_mpv(log):
    try:
        from .reproductor import encontrar_mpv
        ruta = encontrar_mpv()
        log(f"mpv         : {'si' if ruta else 'no'}  {ruta or ''}")
    except Exception as e:
        log(f"mpv         : no se pudo comprobar ({e})")


def _flujo(log, titulo):
    from . import motor

    t0 = time.perf_counter()
    grupos = motor.buscar(titulo, limite=12.0)
    log(f"busqueda    : {len(grupos)} grupos en {time.perf_counter() - t0:.1f}s")
    if not grupos:
        raise RuntimeError("la busqueda no devolvio resultados")
    for g in grupos[:3]:
        con = sum(1 for _s, a in g.coincidencias if a.imagen)
        log(f"   - {g.titulo} [{', '.join(g.sitios())}] portadas={con}")
    g = grupos[0]

    t1 = time.perf_counter()
    bloques = motor.episodios_por_sitio(g, limite=12.0)
    log(f"episodios   : {len(bloques)} bloques en {time.perf_counter() - t1:.1f}s")
    for b in bloques:
        log(f"   - {b['sitio']} rango {b['rango']} ({len(b['epis'])} eps)")
    if not bloques:
        raise RuntimeError("no se pudieron obtener episodios")
    bloque, mayor, total = motor.bloque_mayor(bloques)
    log(f"mejor bloque: {bloque['sitio']} hasta {mayor} ({total} eps)")
    if mayor < 1:
        raise RuntimeError("numeracion de episodios invalida")

    t2 = time.perf_counter()
    streams = motor.streams_del_capitulo(bloques, 1)
    log(f"streams cap1: {len(streams)} en {time.perf_counter() - t2:.1f}s")
    for s in streams[:6]:
        log(f"   - {s.host}")
    if not streams:
        raise RuntimeError("no se resolvieron streams para el capitulo 1")

    t3 = time.perf_counter()
    cands = motor.candidatos_todos(streams, motor.medir(streams))
    log(f"servidores  : {len(cands)} en {time.perf_counter() - t3:.1f}s")
    for c in cands:
        log(f"   - {c['host']} ttfb={c['ttfb_ms']} mbps={c['mbps']}")

    t4 = time.perf_counter()
    n_img = _probar_posters(log, g)
    log(f"posters     : {n_img} descargados en {time.perf_counter() - t4:.1f}s")
    log("RESULTADO   : OK")


def _probar_posters(log, grupo):
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QGuiApplication

    from .tarjetas import CargadorImagenes

    app = QGuiApplication.instance() or QGuiApplication([])
    cargador = CargadorImagenes()
    urls = []
    for _s, a in grupo.coincidencias:
        if a.imagen and a.imagen not in urls:
            urls.append(a.imagen)
    urls = urls[:4]
    if not urls:
        log("   (sin urls de poster)")
        return 0
    estado = {"ok": 0}

    def recibir(url, pix):
        if pix is not None and not pix.isNull():
            estado["ok"] += 1
            log(f"   - {url[-40:]}: {pix.width()}x{pix.height()}")
        else:
            log(f"   - {url[-40:]}: fallo")
        if not cargador._pendientes:
            QTimer.singleShot(0, app.quit)

    for u in urls:
        cargador.obtener(u, recibir)
    QTimer.singleShot(9000, app.quit)
    app.exec()
    return estado["ok"]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    titulo = "frieren"
    if argv and not argv[0].startswith("-"):
        titulo = argv[0]
    log = _Bitacora(_log_path())
    try:
        _info_python(log)
        _info_motor(log)
        _info_mpv(log)
        _flujo(log, titulo)
        log()
        log("Informe completo en " + log.ruta)
        print(log.volcar())
        return 0
    except Exception as e:
        log(f"RESULTADO   : ERROR -> {e}")
        log()
        log(traceback.format_exc())
        print(log.volcar())
        return 1