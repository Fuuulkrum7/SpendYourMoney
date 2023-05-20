import os
import sys
from platform import system

from PyQt5.QtWidgets import QApplication

from info.file_loader import FileLoader
from ui_dev.first_gui import CreateWindow
from ui_dev.settings import set_theme_and_font

if __name__ == '__main__':
    app = QApplication(sys.argv)

    wndw = CreateWindow(app)
    wndw.create_main()
    sys.exit(app.exec_())
