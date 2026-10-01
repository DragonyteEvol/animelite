"""Ejecucion asincrona: envuelve tareas bloqueantes en el QThreadPool."""
import contextlib
import inspect
import io
import traceback

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class _Emisor(QObject):
    exito = Signal(object)
    error = Signal(str)
    progreso = Signal(int, object)
    fin = Signal()


class Tarea(QRunnable):
    """Ejecuta fn(*args, **kwargs) en un hilo del pool.

    Emite exito(resultado), error(mensaje), progreso(pct, texto), fin().
    Si fn acepta un parametro `on_progreso`, se le inyecta una funcion que
    reemite las señales de progreso. El stdout/stderr del motor se captura
    para no ensuciar la consola.
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = dict(kwargs)
        self._emis = _Emisor()
        self.exito = self._emis.exito
        self.error = self._emis.error
        self.progreso = self._emis.progreso
        self.fin = self._emis.fin
        self.cancelada = False
        self._params = inspect.signature(fn).parameters
        if "on_progreso" in self._params:
            self.kwargs["on_progreso"] = self._prog

    def _prog(self, pct, texto=None):
        self.progreso.emit(int(pct), texto)

    def cancelar(self):
        self.cancelada = True

    def run(self):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                resultado = self.fn(*self.args, **self.kwargs)
        except Exception as exc:
            detalle = traceback.format_exc(limit=3)
            self.error.emit(f"{exc}\n{detalle}")
            self.fin.emit()
            return
        self.exito.emit(resultado)
        self.fin.emit()


def lanzar(fn, *args, on_exito=None, on_error=None, on_fin=None,
           on_progreso=None, **kwargs) -> Tarea:
    """Lanza fn en el pool y conecta los callbacks a sus señales."""
    tarea = Tarea(fn, *args, **kwargs)
    if on_exito:
        tarea.exito.connect(on_exito)
    if on_error:
        tarea.error.connect(on_error)
    if on_fin:
        tarea.fin.connect(on_fin)
    if on_progreso:
        tarea.progreso.connect(on_progreso)
    QThreadPool.globalInstance().start(tarea)
    return tarea