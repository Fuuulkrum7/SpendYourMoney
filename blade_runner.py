import sys

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    from ui_dev.menu import CreateWindow
    app = QApplication(sys.argv)

    wndw = CreateWindow(app)
    wndw.create_main()
    sys.exit(app.exec_())