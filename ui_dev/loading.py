import time

from PyQt5 import QtWidgets


class LoadingDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)

        self.loadingLabel = QtWidgets.QLabel('Loading...', self)
        self.loadingLabel.setGeometry(75, 30, 100, 20)

        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(0)
        self.pbar.setValue(0)
        self.pbar.setGeometry(40, 75, 160, 20)

    def start_loading(self):
        self.show()

    def after_load(self):
        # code, data = result
        # print(code)
        self.loadingLabel.setText("Done")
        self.pbar.setMaximum(100)
        self.pbar.setValue(100)
        time.sleep(0.2)
        self.close()
