"""Paletas claro/oscura y generacion de QSS."""
from . import config

PALETAS = {
    "oscuro": {
        "bg": "#0B0B12",
        "surface": "#14141E",
        "surface2": "#1C1C28",
        "surface3": "#232333",
        "border": "#262634",
        "text": "#F2F3F7",
        "dim": "#9A9AB0",
        "faint": "#6B6B80",
        "a1": "#8B5CF6",
        "a2": "#22D3EE",
        "danger": "#F87171",
        "ok": "#4ADE80",
        "sombra": "0,0,0,180",
        "sombra_hover": "124,92,255,150",
        "barra": "#1F1F2C",
        "barra_mano": "#3A3A50",
    },
    "claro": {
        "bg": "#F6F6FA",
        "surface": "#FFFFFF",
        "surface2": "#EFEFF6",
        "surface3": "#E6E6F0",
        "border": "#E0E0EC",
        "text": "#14141E",
        "dim": "#6B6B80",
        "faint": "#9A9AAE",
        "a1": "#7C3AED",
        "a2": "#0891B2",
        "danger": "#DC2626",
        "ok": "#16A34A",
        "sombra": "30,30,60,60",
        "sombra_hover": "124,58,237,90",
        "barra": "#DEDEE8",
        "barra_mano": "#B9B9CC",
    },
}

_TPL = """
QWidget {{
    background: {bg};
    color: {text};
    font-family: "Segoe UI", "Inter", system-ui, sans-serif;
    font-size: 14px;
}}
QToolTip {{
    background: {surface2};
    color: {text};
    border: 1px solid {border};
    padding: 6px 9px;
    border-radius: 6px;
}}

/* ---------- cabecera ---------- */
#cabecera {{
    background: {surface};
    border-bottom: 1px solid {border};
}}
#marca {{
    font-size: 19px;
    font-weight: 700;
    letter-spacing: 1.2px;
    background: transparent;
}}
#estado {{
    color: {dim};
    background: transparent;
}}

/* ---------- buscador ---------- */
#buscador {{
    background: {surface2};
    border: 1px solid {border};
    border-radius: 14px;
    padding: 13px 18px;
    font-size: 15px;
    color: {text};
    selection-background-color: {a1};
}}
#buscador:focus {{
    border: 1px solid {a1};
    background: {surface};
}}
#buscador::placeholder {{
    color: {faint};
}}

/* ---------- botones ---------- */
QPushButton {{
    background: {surface2};
    color: {text};
    border: 1px solid {border};
    border-radius: 11px;
    padding: 10px 16px;
    font-size: 14px;
}}
QPushButton:hover {{
    background: {surface3};
    border: 1px solid {dim};
}}
QPushButton:pressed {{
    background: {surface};
}}
QPushButton:disabled {{
    color: {faint};
    border: 1px solid {border};
}}
#primario {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {a1}, stop:1 {a2});
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}
#primario:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #A78BFA, stop:1 #67E8F9);
}}
#icono {{
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 7px 11px;
    font-size: 15px;
    color: {dim};
}}
#icono:hover {{
    background: {surface2};
    color: {text};
}}

/* ---------- tarjetas ---------- */
#tarjeta {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 14px;
}}
#poster {{
    background: {surface2};
    border: none;
    border-top-left-radius: 13px;
    border-top-right-radius: 13px;
    color: {faint};
    font-size: 12px;
}}
#titulo_card {{
    background: transparent;
    color: {text};
    font-size: 13px;
    font-weight: 600;
    padding: 0px 2px;
}}
#detalle_sub {{
    background: transparent;
    color: {dim};
    font-size: 11px;
}}
#badge {{
    background: {a1};
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 2px 7px;
    font-size: 10px;
    font-weight: 600;
}}
#chip_seccion {{
    background: transparent;
    border: none;
    color: {dim};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.1px;
    padding: 0px 2px 6px 2px;
}}

/* ---------- detalle ---------- */
#titulo_detalle {{
    background: transparent;
    font-size: 30px;
    font-weight: 700;
    letter-spacing: 0.3px;
}}
#hito {{
    background: transparent;
    color: {dim};
    font-size: 13px;
}}
#chip_cap {{
    background: {surface2};
    color: {text};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 7px 0px;
    font-size: 13px;
    min-width: 46px;
}}
#chip_cap:hover {{
    background: {surface3};
    border: 1px solid {a2};
}}
#chip_cap_visto {{
    background: transparent;
    color: {faint};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 7px 0px;
    font-size: 13px;
    min-width: 46px;
}}

/* ---------- servidores ---------- */
#server {{
    background: {surface};
    border: 1px solid {border};
    border-radius: 11px;
}}
#server:hover {{
    border: 1px solid {a1};
}}
#lat {{
    background: transparent;
    color: {ok};
    font-size: 12px;
    font-weight: 600;
}}
#lat_malo {{
    background: transparent;
    color: {faint};
    font-size: 12px;
}}

/* ---------- varios ---------- */
#vacio_tit {{
    background: transparent;
    font-size: 22px;
    font-weight: 600;
    color: {dim};
}}
#vacio_sub {{
    background: transparent;
    font-size: 13px;
    color: {faint};
}}
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {barra_mano};
    border-radius: 5px;
    min-height: 40px;
}}
QScrollBar::handle:vertical:hover {{
    background: {dim};
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
}}
QScrollBar::add-page, QScrollBar::sub-page {{
    background: transparent;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {barra_mano};
    border-radius: 5px;
    min-width: 40px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: transparent;
}}
QProgressBar {{
    background: {barra};
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {a1}, stop:1 {a2});
    border-radius: 3px;
}}
QDialog {{
    background: {bg};
}}
QMessageBox {{
    background: {bg};
}}
"""


def paleta() -> dict:
    nombre = config.config().get("tema", "oscuro")
    return PALETAS.get(nombre, PALETAS["oscuro"])


def tema_actual() -> str:
    return config.config().get("tema", "oscuro")


def alternar_tema() -> str:
    nuevo = "claro" if tema_actual() == "oscuro" else "oscuro"
    config.guardar({"tema": nuevo})
    return nuevo


def qss(nombre: str = None) -> str:
    p = PALETAS.get(nombre or tema_actual(), PALETAS["oscuro"])
    return _TPL.format(**p)


def acento() -> str:
    return paleta()["a1"]


def acento2() -> str:
    return paleta()["a2"]