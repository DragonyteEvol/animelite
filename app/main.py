"""Punto de entrada de la app de escritorio."""
import sys

from PySide6.QtWidgets import QApplication

from . import i18n, tema
from .ventana import Ventana


def main():
    if "--selftest" in sys.argv:
        from .selftest import main as selftest_main
        raise SystemExit(selftest_main(sys.argv[1:]))
    i18n.cargar()
    app = QApplication(sys.argv)
    app.setApplicationName("animelite")
    app.setStyleSheet(tema.qss())
    w = Ventana()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()