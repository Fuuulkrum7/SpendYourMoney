import sys

from PyQt5.QtWidgets import QApplication
from ui_dev.first_gui import CreateWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # with open("ui_dev/styles.css", "r") as style:
    #     app.setStyleSheet(style.read())

    wndw = CreateWindow(app)
    wndw.create_main(app)
    sys.exit(app.exec_())
