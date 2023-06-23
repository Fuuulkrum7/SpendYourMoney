import sys

from PyQt5.QtWidgets import QApplication

from ui_dev.menu import CreateWindow
from setup import load_settings

if __name__ == '__main__':
    load_settings()
    app = QApplication(sys.argv)

    wndw = CreateWindow(app)
    wndw.create_main()
    sys.exit(app.exec_())
