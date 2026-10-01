"""Tarjetas de poster, lienzo con rejilla fluida y cache de imagenes."""
import os
from urllib.parse import urlparse

from PySide6.QtCore import (
    QEasingCurve, QPointF, QPropertyAnimation, QRectF, Qt, QTimer, Signal,
)
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGraphicsProxyWidget, QGraphicsScene, QGraphicsView, QLabel,
    QSizePolicy, QVBoxLayout, QWidget,
)

from . import tema


def _cache_dir() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    d = os.path.join(base, "animelite", "cache")
    os.makedirs(d, exist_ok=True)
    return d


class CargadorImagenes:
    """Descarga y cachea portadas (QNetworkAccessManager, asincrono)."""

    def __init__(self, parent=None):
        from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
        self._memoria = {}
        self._pendientes = {}
        self._nam = QNetworkAccessManager(parent)
        self._req = QNetworkRequest
        self._parent = parent

    def obtener(self, url: str, al_recibir) -> None:
        """Si la imagen esta en cache la entrega ya; si no, la descarga."""
        if not url:
            return
        pix = self._memoria.get(url)
        if pix is not None:
            al_recibir(url, pix)
            return
        archivo = self._ruta_cache(url)
        if os.path.isfile(archivo):
            try:
                pix = QPixmap(archivo)
                if not pix.isNull():
                    self._memoria[url] = pix
                    al_recibir(url, pix)
                    return
            except Exception:
                pass
        if url in self._pendientes:
            self._pendientes[url].append(al_recibir)
            return
        self._pendientes[url] = [al_recibir]
        req = self._req(url)
        resp = self._nam.get(req)
        resp.finished.connect(lambda r, u=url: self._al_terminar(r, u))

    def _al_terminar(self, resp, url):
        callbacks = self._pendientes.pop(url, [])
        try:
            if resp.error() is not None or resp.isFinished() is None:
                return
            datos = resp.readAll()
            pix = QPixmap()
            if pix.loadFromData(datos):
                self._memoria[url] = pix
                self._guardar(url, pix)
                for cb in callbacks:
                    cb(url, pix)
        except Exception:
            pass

    @staticmethod
    def _ruta_cache(url):
        import hashlib
        h = hashlib.md5(url.encode("utf-8")).hexdigest()
        ext = os.path.splitext(urlparse(url).path)[1][:6] or ".img"
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            ext = ".img"
        return os.path.join(_cache_dir(), h + ext)

    @staticmethod
    def _guardar(url, pix):
        try:
            pix.save(CargadorImagenes._ruta_cache(url))
        except Exception:
            pass


class CardPoster(QFrame):
    """Tarjeta de poster: imagen 2:3, titulo, badge de sitio/capitulo."""

    clicked = Signal(object)
    _hover = Signal(bool, object)

    ANCHO = 168
    ALTO_IMG = 250
    ALTO = 250 + 54

    def __init__(self, titulo, imagen="", subtitulo="", badge="", payload=None,
                 parent=None):
        super().__init__(parent)
        self.payload = payload
        self.setObjectName("tarjeta")
        self.setFixedSize(self.ANCHO, self.ALTO)
        self.setCursor(Qt.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 6)
        lay.setSpacing(4)

        self.img = QLabel()
        self.img.setObjectName("poster")
        self.img.setFixedSize(self.ANCHO - 16, self.ALTO_IMG)
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setScaledContents(False)
        lay.addWidget(self.img)

        self.tit = QLabel(_cortar(titulo, 30))
        self.tit.setObjectName("titulo_card")
        self.tit.setFixedHeight(32)
        self.tit.setWordWrap(True)
        self.tit.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        lay.addWidget(self.tit)

        pie = QWidget()
        pie.setFixedHeight(18)
        pl = QHBox(pie)
        pl.setContentsMargins(2, 0, 2, 0)
        if subtitulo:
            st = QLabel(subtitulo)
            st.setObjectName("detalle_sub")
            pl.addWidget(st)
        pl.addStretch()
        if badge:
            b = QLabel(badge)
            b.setObjectName("badge")
            pl.addWidget(b)
        lay.addWidget(pie)

    def set_imagen(self, pix: QPixmap) -> None:
        p = QPixmap(pix)
        p = p.scaled(self.img.width(), self.img.height(),
                     Qt.KeepAspectRatioByExpanding,
                     Qt.SmoothTransformation)
        x = (p.width() - self.img.width()) // 2
        y = (p.height() - self.img.height()) // 2
        recortada = p.copy(x, y, self.img.width(), self.img.height())
        self.img.setPixmap(recortada)

    def enterEvent(self, e):
        self._hover.emit(True, self)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover.emit(False, self)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.payload)
        super().mousePressEvent(e)


class QHBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QHBoxLayout
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

    def addWidget(self, w):
        lay = self.layout()
        lay.addWidget(w)

    def addStretch(self):
        lay = self.layout()
        lay.addStretch()


def _cortar(t: str, n: int) -> str:
    t = t or ""
    return t if len(t) <= n else t[: n - 1] + "…"


class Lienzo(QGraphicsView):
    """Rejilla fluida de tarjetas en una escena, con hover que escala."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._escena = QGraphicsScene(self)
        self.setScene(self._escena)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Scrolling)
        self._items = []          # [(proxy, widget)]
        self._anims = {}
        self._gap = 18
        self._margen = 6

    def limpiar(self):
        for proxy, _w in self._items:
            self._escena.removeItem(proxy)
            proxy.widget().deleteLater()
        self._items.clear()
        self._anims.clear()

    def agregar(self, widget: CardPoster):
        proxy = self._escena.addWidget(widget)
        proxy.setFlag(QGraphicsProxyWidget.ItemIsSelectable, False)
        self._hover = widget._hover
        widget._hover.connect(self._escalar)
        self._items.append((proxy, widget))
        self._reubicar()
        return proxy

    def _escalar(self, hover, widget):
        proxy = next((p for p, w in self._items if w is widget), None)
        if proxy is None:
            return
        objetivo = 1.045 if hover else 1.0
        anim = QPropertyAnimation(proxy, b"scale")
        anim.setDuration(140)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(proxy.scale())
        anim.setEndValue(objetivo)
        anim.start()
        self._anims[widget] = anim
        # centra el crecimiento
        centro = widget.rect().center()
        proxy.setPos(proxy.pos().x() - (proxy.scale() - objetivo) * centro.x() / 2,
                     proxy.pos().y() - (proxy.scale() - objetivo) * centro.y() / 2)

    def _reubicar(self):
        if not self._items:
            self._escena.setSceneRect(QRectF())
            return
        w = self.viewport().width() - self._margen * 2
        ancho = CardPoster.ANCHO + self._gap
        cols = max(1, int((w + self._gap) // ancho))
        for i, (proxy, _widget) in enumerate(self._items):
            col, fila = i % cols, i // cols
            x = self._margen + col * ancho
            y = self._margen + fila * (CardPoster.ALTO + self._gap)
            proxy.setPos(QPointF(x, y))
        filas = (len(self._items) + cols - 1) // cols
        alto = self._margen * 2 + filas * (CardPoster.ALTO + self._gap)
        ancho_total = self._margen * 2 + cols * (CardPoster.ANCHO + self._gap) - self._gap
        self._escena.setSceneRect(QRectF(0, 0, ancho_total, alto))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        QTimer.singleShot(0, self._reubicar)

    def scrollToTop(self):
        self.verticalScrollBar().setValue(0)