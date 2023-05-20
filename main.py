import os
import sys
from platform import system

from PyQt5.QtWidgets import QApplication

from info.file_loader import FileLoader
from ui_dev.first_gui import CreateWindow
from ui_dev.settings import set_theme_and_font

if __name__ == '__main__':
    app = QApplication(sys.argv)

    sep = "\\" if system() == "Windows" else "/"
    folder = os.path.abspath("security_info_tabs.py").split(sep)
    folder.pop()
    path = sep.join(folder)
    settings = FileLoader.get_json(
        path + "/info/files/.current_settings.json"
    )
    if not (settings is None):
        set_theme_and_font(app, settings)
    wndw = CreateWindow(app)
    wndw.create_main()
    sys.exit(app.exec_())
