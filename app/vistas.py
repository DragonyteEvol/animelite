"""Vistas de la app: Inicio, Resultados, Detalle y dialogo de servidores."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from . import historial, i18n, tema
from .tarjetas import CardPoster, Lienzo


class Vista(QWidget):
    def __init__(self, ventana, parent=None):
        super().__init__(parent)
        self.v = ventana
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def retraducir(self):
        pass


class VistaInicio(Vista):
    enviada = Signal(str)

    def __init__(self, ventana, parent=None):
        super().__init__(ventana, parent)
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(14)

        # ---- buscador centrado
        centro = QVBoxLayout()
        centro.setSpacing(12)
        self.entrada = QLineEdit()
        self.entrada.setObjectName("buscador")
        self.entrada.setMinimumHeight(58)
        self.entrada.returnPressed.connect(self._enviar)
        centro.addWidget(self.entrada)

        self.btn = QPushButton()
        self.btn.setObjectName("primario")
        self.btn.setMinimumHeight(46)
        self.btn.setMaximumWidth(220)
        self.btn.clicked.connect(self._enviar)
        centro.addWidget(self.btn, 0, Qt.AlignHCenter)

        self.tit = QLabel()
        self.tit.setObjectName("vacio_titulo")
        self.tit.setAlignment(Qt.AlignCenter)
        centro.addSpacing(22)
        centro.addWidget(self.tit)
        self.sub = QLabel()
        self.sub.setObjectName("vacio_sub")
        self.sub.setAlignment(Qt.AlignCenter)
        centro.addWidget(self.sub)
        raiz.addLayout(centro)

        # ---- seguir viendo
        self.chip = QLabel()
        self.chip.setObjectName("chip_seccion")
        raiz.addWidget(self.chip)
        self.lienzo = Lienzo()
        self.lienzo.setMinimumHeight(150)
        raiz.addWidget(self.lienzo, 1)

        self.retraducir()

    def _enviar(self):
        q = self.entrada.text().strip()
        if q:
            self.enviada.emit(q)

    def cargar_seguir(self):
        self.lienzo.limpiar()
        datos = historial.recientes(6)
        for d in datos:
            titulo = d.get("titulo", "")
            imagen = d.get("imagen", "")
            cap = d.get("cap")
            sub = f"{d.get('sitio','')}"
            badge = i18n.tr("cap_de", cap=cap) if cap else ""
            card = CardPoster(titulo, imagen, sub, badge,
                              payload={"tipo": "historial", "dato": d})
            card.clicked.connect(self.v.abrir_historial)
            self.lienzo.agregar(card)
            self._cargar_posters(card, imagen)
        self.lienzo.setVisible(bool(datos))

    def _cargar_posters(self, card, imagen):
        if not imagen:
            return
        self.v.cargador.obtener(imagen, lambda u, p: card.set_imagen(p))

    def retraducir(self):
        self.entrada.setPlaceholderText(i18n.tr("buscar_ph"))
        self.btn.setText(i18n.tr("buscar_btn"))
        self.tit.setText(i18n.tr("vacio_titulo"))
        self.sub.setText(i18n.tr("vacio_sub"))
        self.chip.setText(i18n.tr("siguiendo").upper())


class VistaResultados(Vista):
    elegida = Signal(object)

    def __init__(self, ventana, parent=None):
        super().__init__(ventana, parent)
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(10)

        self.chip = QLabel()
        self.chip.setObjectName("chip_seccion")
        raiz.addWidget(self.chip)

        self.lienzo = Lienzo()
        raiz.addWidget(self.lienzo, 1)

        self.vacio = QLabel()
        self.vacio.setObjectName("vacio_sub")
        self.vacio.setAlignment(Qt.AlignCenter)
        self.vacio.setVisible(False)
        raiz.addWidget(self.vacio)

    def mostrar(self, grupos):
        self.lienzo.limpiar()
        self.lienzo.setVisible(bool(grupos))
        self.vacio.setVisible(not grupos)
        if not grupos:
            self.chip.setText(i18n.tr("sin_resultados").upper())
            self.vacio.setText(i18n.tr("sin_resultados_sub"))
            return
        self.chip.setText(f"{i18n.tr('buscar_btn').upper()}  ·  "
                          f"{len(grupos)}")
        for g in grupos:
            anime = next((a for _s, a in g.coincidencias if a.imagen), None)
            if anime is None:
                anime = g.coincidencias[0][1] if g.coincidencias else None
            if anime is None:
                continue
            sub = " · ".join(g.sitios()[:3])
            card = CardPoster(g.titulo, anime.imagen, sub, "",
                              payload={"tipo": "grupo", "dato": g})
            card.clicked.connect(self.elegida.emit)
            self.lienzo.agregar(card)
            if anime.imagen:
                self.v.cargador.obtener(
                    anime.imagen, lambda u, p, c=card: c.set_imagen(p))
        self.lienzo.scrollToTop()

    def retraducir(self):
        pass


class VistaDetalle(Vista):
    cap_elegido = Signal(int)

    def __init__(self, ventana, parent=None):
        super().__init__(ventana, parent)
        self.grupo = None
        self.mayor = 0
        self.total = 0

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(12)

        # ---- cabecera del anime
        cab = QHBoxLayout()
        cab.setSpacing(18)

        self.poster = QLabel()
        self.poster.setObjectName("poster")
        self.poster.setFixedSize(190, 285)
        self.poster.setAlignment(Qt.AlignCenter)
        cab.addWidget(self.poster)

        info = QVBoxLayout()
        info.setSpacing(6)
        self.titulo = QLabel()
        self.titulo.setObjectName("titulo_detalle")
        self.titulo.setWordWrap(True)
        info.addWidget(self.titulo)
        self.hito = QLabel()
        self.hito.setObjectName("hito")
        info.addWidget(self.hito)

        self.chip_seccion = QLabel()
        self.chip_seccion.setObjectName("chip_seccion")
        info.addSpacing(8)
        info.addWidget(self.chip_seccion)
        raiz.addLayout(cab)

        # ---- capitulos
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.contenedor = QWidget()
        self.grid = QGridLayout(self.contenedor)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(8)
        self.scroll.setWidget(self.contenedor)
        self.scroll.setFixedHeight(130)
        raiz.addWidget(self.scroll)

        # ---- pie
        pie = QHBoxLayout()
        self.estado = QLabel()
        self.estado.setObjectName("hito")
        pie.addWidget(self.estado)
        pie.addStretch()
        self.btn_servidores = QPushButton()
        self.btn_servidores.setEnabled(False)
        self.btn_servidores.clicked.connect(
            lambda: self.v.mostrar_servidores(self))
        pie.addWidget(self.btn_servidores)
        raiz.addLayout(pie)

    def mostrar(self, grupo):
        self.grupo = grupo
        anime = grupo.coincidencias[0][1]
        self.titulo.setText(grupo.titulo)
        self.poster.setText(i18n.tr("sin_imagen"))
        if anime.imagen:
            self.v.cargador.obtener(
                anime.imagen, lambda u, p: self.poster.setPixmap(
                    p.scaled(self.poster.size(), Qt.KeepAspectRatioByExpanding,
                             Qt.SmoothTransformation)))
        self.estado.setText(i18n.tr("cargando_episodios"))
        self.btn_servidores.setEnabled(False)
        self._limpiar_caps()

    def poner_capitulos(self, bloques):
        mayor, total = self.v.datos_capitulos(bloques)
        self.mayor, self.total = mayor, total
        sitios = sorted({b["sitio"] for b in bloques})
        n_caps = len({e.numero for b in bloques for e in b["epis"]})
        self.hito.setText(" · ".join(sitios) + f"   |   {total} {i18n.tr('vistas')}")
        self.estado.setText("")
        self._limpiar_caps()
        self.chip_seccion.setText(i18n.tr("capitulos").upper())
        vistos = {h.get("cap") for h in historial.recientes(40)
                  if h.get("slug") == anime_slug(self.grupo)}
        cols = 14
        mostrados = min(mayor, 160)
        for n in range(1, mostrados + 1):
            b = QPushButton(str(n))
            b.setObjectName("chip_cap_visto" if n in vistos else "chip_cap")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, cap=n: self.cap_elegido.emit(cap))
            self.grid.addWidget(b, (n - 1) // cols, (n - 1) % cols)
        if mostrados < mayor:
            cola = QLabel(i18n.tr("capitulos") + f" 1-{mostrados} / {mayor}")
            cola.setObjectName("hito")
            self.grid.addWidget(cola, mostrados // cols + 1, 0)

    def _limpiar_caps(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()


def anime_slug(grupo) -> str:
    if grupo and grupo.coincidencias:
        return grupo.coincidencias[0][1].slug
    return ""


class DialogoServidores(QDialog):
    """Lista minimal de servidores con su latencia; clic para reproducir."""

    elegido = Signal(object)

    def __init__(self, candidatos, titulo="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumWidth(420)
        self.setStyleSheet(tema.qss())

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(18, 18, 18, 18)
        raiz.setSpacing(10)

        cab = QLabel(f"{i18n.tr('servidores').upper()}  ·  {len(candidatos)}")
        cab.setObjectName("chip_seccion")
        raiz.addWidget(cab)

        if not candidatos:
            vacio = QLabel(i18n.tr("sin_respuesta"))
            vacio.setObjectName("vacio_sub")
            vacio.setAlignment(Qt.AlignCenter)
            vacio.setMinimumHeight(80)
            raiz.addWidget(vacio)
            return

        for c in candidatos:
            f = QFrame()
            f.setObjectName("server")
            f.setCursor(Qt.PointingHandCursor)
            lay = QHBoxLayout(f)
            lay.setContentsMargins(14, 10, 14, 10)
            h = QLabel(c.get("host", "?"))
            h.setObjectName("titulo_card")
            lay.addWidget(h)
            lay.addStretch()
            ms = c.get("ttfb_ms")
            if ms is None:
                lat = QLabel(i18n.tr("sin_medir"))
                lat.setObjectName("lat_malo")
            else:
                lat = QLabel(f"{int(ms)} ms  ·  "
                             f"{c.get('mbps') or 0:.2f} Mbps")
                lat.setObjectName("lat")
            lay.addWidget(lat)

            def _click(_=False, cc=c):
                self.elegido.emit(cc)

            f.mousePressEvent = _click
            raiz.addWidget(f)

        btn = QPushButton(i18n.tr("volver"))
        btn.clicked.connect(self.accept)
        raiz.addWidget(btn, 0, Qt.AlignRight)