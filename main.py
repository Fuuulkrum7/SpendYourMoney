import sys

from PyQt5.QtWidgets import QApplication

from ui_dev.menu import CreateWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    wndw = CreateWindow(app)
    wndw.create_main()
    sys.exit(app.exec_())
