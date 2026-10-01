"""Ventana principal: cabecera, pila de vistas y orquestacion."""
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMessageBox, QProgressBar,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from . import historial, i18n, motor, tema, worker
from .reproductor import reproducir
from .tarjetas import CargadorImagenes
from .vistas import (
    DialogoServidores, VistaDetalle, VistaInicio, VistaResultados,
)


class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("animelite")
        self.resize(1240, 800)
        self.setMinimumSize(940, 620)

        self.cargador = CargadorImagenes(self)
        self.tarea = None
        self.grupo_actual = None
        self.bloques = []
        self.candidatos = []
        self.cap_actual = 0
        self._streams_actuales = []
        self.tarea_ep = None
        self.tarea_streams = None

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(self._cabecera())

        self.stack = QStackedWidget()
        raiz.addWidget(self.stack, 1)

        # pie: progreso
        pie = QWidget()
        pl = QHBoxLayout(pie)
        pl.setContentsMargins(20, 6, 20, 12)
        self.progreso = QProgressBar()
        self.progreso.setRange(0, 100)
        self.progreso.setValue(0)
        self.progreso.setTextVisible(False)
        self.progreso.setMaximumWidth(220)
        self.progreso.setVisible(False)
        pl.addWidget(self.progreso)
        pl.addStretch()
        self.pie_info = QLabel()
        self.pie_info.setObjectName("hito")
        pl.addWidget(self.pie_info)
        raiz.addWidget(pie)

        # ---- vistas
        self.inicio = VistaInicio(self)
        self.resultados = VistaResultados(self)
        self.detalle = VistaDetalle(self)

        self.inicio.enviada.connect(self.buscar)
        self.resultados.elegida.connect(self.abrir_grupo)
        self.detalle.cap_elegido.connect(self.reproducir_cap)

        self.stack.addWidget(self.inicio)
        self.stack.addWidget(self.resultados)
        self.stack.addWidget(self.detalle)
        self.inicio.cargar_seguir()
        self.ir_inicio()

    # ------------------------------------------------------------- cabecera
    def _cabecera(self):
        cab = QWidget()
        cab.setObjectName("cabecera")
        cab.setFixedHeight(62)
        lay = QHBoxLayout(cab)
        lay.setContentsMargins(18, 8, 14, 8)
        lay.setSpacing(10)

        self.btn_atras = QPushButton("←")
        self.btn_atras.setObjectName("icono")
        self.btn_atras.setToolTip(i18n.tr("volver"))
        self.btn_atras.clicked.connect(self.ir_atras)
        self.btn_atras.setVisible(False)
        lay.addWidget(self.btn_atras)

        self.marca = QLabel("animelite")
        self.marca.setObjectName("marca")
        lay.addWidget(self.marca)

        self.estado = QLabel("")
        self.estado.setObjectName("estado")
        lay.addWidget(self.estado)
        lay.addStretch()

        self.btn_tema = QPushButton("☾")
        self.btn_tema.setObjectName("icono")
        self.btn_tema.setFixedWidth(42)
        self.btn_tema.clicked.connect(self.cambiar_tema)
        lay.addWidget(self.btn_tema)

        self.btn_idioma = QPushButton("EN" if i18n.idioma() == "es" else "ES")
        self.btn_idioma.setObjectName("icono")
        self.btn_idioma.setFixedWidth(46)
        self.btn_idioma.clicked.connect(self.cambiar_idioma)
        lay.addWidget(self.btn_idioma)
        return cab

    # ----------------------------------------------------------- navegacion
    def ir_inicio(self):
        self.stack.setCurrentWidget(self.inicio)
        self.btn_atras.setVisible(False)
        self.estado.setText("")
        self.inicio.cargar_seguir()

    def ir_atras(self):
        if self.stack.currentWidget() is self.detalle:
            self.stack.setCurrentWidget(self.resultados)
            self.btn_atras.setVisible(True)
        else:
            self.ir_inicio()

    # -------------------------------------------------------------- acciones
    def cambiar_tema(self):
        nuevo = tema.alternar_tema()
        QApplication.instance().setStyleSheet(tema.qss(nuevo))
        self.btn_tema.setText("☀" if nuevo == "oscuro" else "☾")
        self._reestilizar()

    def cambiar_idioma(self):
        nuevo = "en" if i18n.idioma() == "es" else "es"
        i18n.fijar(nuevo)
        from . import config
        config.guardar({"idioma": nuevo})
        self.btn_idioma.setText("EN" if nuevo == "es" else "ES")
        self.inicio.retraducir()
        if self.stack.currentWidget() is self.resultados:
            self.resultados.retraducir()
        self.detalle.retraducir()

    def _reestilizar(self):
        """Redibuja vistas caches que dependian del tema."""
        if self.stack.currentWidget() is self.inicio:
            self.inicio.cargar_seguir()

    def buscar(self, query):
        if self.tarea:
            self.tarea.cancelar()
        self.stack.setCurrentWidget(self.resultados)
        self.resultados.lienzo.limpiar()
        self.estado.setText(i18n.tr("buscando"))
        self.progreso.setVisible(True)
        self.progreso.setRange(0, 0)   # indeterminado
        self.inicio.entrada.setText(query)
        self.tarea = worker.lanzar(
            motor.buscar, query,
            on_exito=self._resultados,
            on_error=self._error,
            on_fin=self._fin,
        )

    def _resultados(self, grupos):
        self.resultados.mostrar(grupos)

    def abrir_grupo(self, payload):
        grupo = payload.get("dato")
        if not grupo:
            return
        self.grupo_actual = grupo
        self.bloques = []
        self.candidatos = []
        self.cap_actual = 0
        self.detalle.btn_servidores.setEnabled(False)
        self.detalle.mostrar(grupo)
        self.stack.setCurrentWidget(self.detalle)
        self.btn_atras.setVisible(True)

        if self.tarea_ep:
            self.tarea_ep.cancelar()
        self.estado.setText(i18n.tr("cargando_episodios"))
        self.progreso.setVisible(True)
        self.progreso.setRange(0, 0)
        self.tarea_ep = worker.lanzar(
            motor.episodios_por_sitio, grupo,
            on_exito=self._episodios,
            on_error=self._error,
            on_fin=self._fin,
        )

    def _episodios(self, bloques):
        self.bloques = bloques or []
        self.detalle.poner_capitulos(self.bloques)

    def datos_capitulos(self, bloques):
        _b, mayor, total = motor.bloque_mayor(bloques)
        return mayor, total

    def reproducir_cap(self, cap):
        if not self.bloques:
            return
        self.cap_actual = cap
        self.candidatos = []
        self.detalle.btn_servidores.setEnabled(False)
        self.estado.setText(i18n.tr("resolviendo", cap=cap))
        self.progreso.setVisible(True)
        self.progreso.setRange(0, 100)
        self.progreso.setValue(0)

        if self.tarea_streams:
            self.tarea_streams.cancelar()

        self.tarea_streams = worker.lanzar(
            motor.streams_del_capitulo, self.bloques, cap,
            on_progreso=self._prog,
            on_exito=self._streams,
            on_error=self._error,
            on_fin=self._fin,
        )

    def _streams(self, streams):
        self._streams_actuales = streams  # guardar para emparejar
        if not streams:
            self.estado.setText(i18n.tr("sin_servidores"))
            return
        self.estado.setText(i18n.tr("midiendo"))
        self.progreso.setRange(0, 0)
        worker.lanzar(
            motor.medir, streams,
            on_exito=self._medidos,
            on_error=self._error,
            on_fin=self._fin,
        )

    def _medidos(self, medidos):
        self.candidatos = motor.candidatos_todos(
            self._streams_actuales or [], medidos)
        self.detalle.btn_servidores.setEnabled(bool(self.candidatos))
        self._marcar_historial()
        if self.candidatos:
            self._abrir_candidato(motor.mejor(self.candidatos))
        else:
            self.estado.setText(i18n.tr("sin_respuesta"))

    def _marcar_historial(self):
        if not self.grupo_actual or not self.cap_actual:
            return
        anime = self.grupo_actual.coincidencias[0][1]
        historial.registrar(anime, self.cap_actual)

    def mostrar_servidores(self, vista):
        dlg = DialogoServidores(self.candidatos, self.grupo_actual.titulo, self)
        dlg.elegido.connect(self._abrir_candidato)
        dlg.exec()

    def _abrir_candidato(self, cand):
        stream = cand.get("stream")
        url = cand.get("url") or (stream.url if stream else "")
        if not url:
            return
        referer = stream.referer if stream else ""
        titulo = f"{self.grupo_actual.titulo} - {i18n.tr('cap_de', cap=self.cap_actual)}"
        ok = reproducir(url, referer=referer, titulo=titulo)
        if ok:
            self.estado.setText(i18n.tr("reproducir") + " " +
                                str(self.cap_actual))
        else:
            QMessageBox.information(
                self, "mpv",
                i18n.tr("mpv_falta"))

    def abrir_historial(self, payload):
        d = payload.get("dato") or {}
        url = d.get("url")
        if not url:
            return
        from core.modelo import Anime
        a = Anime(sitio=d.get("sitio", ""), titulo=d.get("titulo", ""),
                  slug=d.get("slug", ""), url=url, imagen=d.get("imagen", ""))
        g = motor.Grupo(d.get("titulo", ""), [])
        s_mod = _modulo_de(d.get("sitio", ""))
        g.coincidencias = [(s_mod, a)]
        self.abrir_grupo({"tipo": "grupo", "dato": g})

    # -------------------------------------------------------------- comunes
    def _prog(self, pct, texto=None):
        self.progreso.setRange(0, 100)
        self.progreso.setValue(pct)
        if texto:
            self.estado.setText(texto)

    def _fin(self):
        if self.tarea is None or not self.tarea.cancelada:
            self.progreso.setVisible(False)
            self.progreso.setRange(0, 100)
            self.estado.setText("")

    def _error(self, msg):
        self.progreso.setVisible(False)
        self.estado.setText("error")
        print("GUI error:", msg)


def _modulo_de(nombre):
    """Devuelve el modulo de sitio correspondiente (o el primero disponible)."""
    try:
        from sitios import SITIOS
        for s in SITIOS:
            if s.__name__.endswith("." + nombre):
                return s
        return SITIOS[0]
    except Exception:
        return None


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(tema.qss())
    w = Ventana()
    w.show()
    sys_exit = app.exec()
    raise SystemExit(sys_exit)