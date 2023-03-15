import os
import sys

import PyQt5
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot, QRunnable, QThreadPool
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton
from PyQt5.QtWidgets import QMessageBox

from api_requests.get_security import GetSecurity
from api_requests.load_all_securities import LoadAllSecurities
from api_requests.security_getter import StandardQuery
from api_requests.user_methods import CheckUser, CreateUser
from info.user import User
from securities.securities import SecurityInfo, Security

folder = 'platforms'
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = folder


class LoginWindow(QtWidgets.QDialog):
    loginval: QLineEdit
    passwordval: QLineEdit
    newtokenval: QLineEdit

    layout_main: QtWidgets.QVBoxLayout
    upper_layout: QtWidgets.QVBoxLayout
    lower_layout: QtWidgets.QHBoxLayout

    verticalGroupBox: QtWidgets.QGroupBox

    def __init__(self, on_reg, parent):
        super(LoginWindow, self).__init__(parent)
        self.horizontalGroupBox = None
        self.creater: CreateWindow = on_reg
        self.setWindowTitle("SpendYourMoney")

        self.threadpool = QThreadPool()

        self.setWindowFlags(self.windowFlags() | PyQt5.QtCore.Qt.Window)
        self.setWindowModality(PyQt5.QtCore.Qt.WindowModal)

        self.setup_login_ui()

    def setup_login_ui(self):
        self.verticalGroupBox = QtWidgets.QGroupBox("Sign in", self)
        self.layout_main = QtWidgets.QVBoxLayout(self)
        self.layout_main.addWidget(self.verticalGroupBox)

        self.upper_layout = QtWidgets.QVBoxLayout(self.verticalGroupBox)

        self.loginval = QLineEdit(self)
        self.upper_layout.addWidget(self.loginval)
        self.loginval.setPlaceholderText("login")

        self.passwordval = QLineEdit(self)
        self.passwordval.setPlaceholderText("password")
        self.passwordval.setEchoMode(QLineEdit.Password)
        self.upper_layout.addWidget(self.passwordval)

        button_login = QtWidgets.QPushButton("Login", self)
        button_login.clicked.connect(self.handle_login)
        self.upper_layout.addWidget(button_login)

        self.horizontalGroupBox = QtWidgets.QGroupBox("Registration", self)
        button_register_instead = QtWidgets.QPushButton("Go to registration",
                                                        self)
        button_register_instead.clicked.connect(self.creater.create_reg)
        self.layout_main.addWidget(self.horizontalGroupBox)
        self.lower_layout = QtWidgets.QHBoxLayout(self.horizontalGroupBox)
        self.lower_layout.addWidget(button_register_instead)

    def on_finish(self, code):
        if code in (200, 201, 202, 211):
            self.creater.after_enter()
        elif code == 100:
            QMessageBox.warning(self, 'Error', 'Bad user or password')
        elif code == 250:
            QMessageBox.warning(self, 'Error', "User doesn't exists")
        elif code == 300:
            QMessageBox.warning(self, 'Error', 'Something went wrong')
        elif code in (400, 500):
            QMessageBox.warning(self, 'Error', "Invalid token")

    def create_user(self, code, user):
        self.creater.user = user
        self.threadpool.start(Worker(data=code, on_finish=self.on_finish))

    def handle_login(self):
        CheckUser(self.loginval.text(), self.passwordval.text(),
                  self.create_user).start()

    def closeEvent(self, evnt):
        evnt.ignore()
        quit(0)


class RegisterWindow(QtWidgets.QDialog):
    newloginval: QLineEdit
    newpasswordval: QLineEdit
    newtokenval: QLineEdit

    def __init__(self, on_login, parent):
        super(RegisterWindow, self).__init__(parent)
        self.horizontalGroupBox = QtWidgets.QGroupBox("Sign in", self)
        self.verticalGroupBox = QtWidgets.QGroupBox("Registration", self)
        self.creater: CreateWindow = on_login
        self.setWindowTitle("SpendYourMoney")
        self.setup_register_ui()
        self.threadpool = QThreadPool()

        self.setWindowFlags(self.windowFlags() | PyQt5.QtCore.Qt.Window)
        self.setParent(parent)
        self.setWindowModality(PyQt5.QtCore.Qt.WindowModal)

    def setup_register_ui(self):
        layout_main = QtWidgets.QVBoxLayout(self)
        layout_main.addWidget(self.verticalGroupBox)
        layout = QtWidgets.QVBoxLayout(self.verticalGroupBox)
        self.newloginval = QLineEdit(self)
        self.newloginval.setPlaceholderText("login")
        layout.addWidget(self.newloginval)
        self.newpasswordval = QLineEdit(self)
        self.newpasswordval.setPlaceholderText("password")
        self.newpasswordval.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.newpasswordval)
        self.newtokenval = QLineEdit(self)
        self.newtokenval.setPlaceholderText("token")
        layout.addWidget(self.newtokenval)
        button_register = QtWidgets.QPushButton("Register", self)
        button_register.clicked.connect(self.handle_register)
        layout.addWidget(button_register)

        button_login_instead = QtWidgets.QPushButton("Back to login",
                                                     self)
        button_login_instead.clicked.connect(self.creater.create_login)
        layout_main.addWidget(self.horizontalGroupBox)
        layout = QtWidgets.QHBoxLayout(self.horizontalGroupBox)
        layout.addWidget(button_login_instead)

    def on_finish(self, code):
        print(code)
        if code in (110, 101, 102):
            QMessageBox.warning(self, 'Error', "User already exists")
        elif code == 200:
            self.creater.after_enter()
        elif code in (300, 500):
            QMessageBox.warning(self, 'Error', 'Something went wrong')

    def after_create(self, code: int, loaded_data):
        self.creater.user = loaded_data
        self.threadpool.start(Worker(data=code, on_finish=self.on_finish))

    def handle_register(self):
        CreateUser(
            User(
                username=self.newloginval.text(),
                token=self.newtokenval.text()
            ),
            self.newpasswordval.text(),
            self.after_create
        ).start()

    def closeEvent(self, evnt):
        evnt.ignore()
        quit(0)


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.textbox = QLineEdit(self)
        self.button = QPushButton('Find security', self)
        self.load_all_btn = QPushButton('Load all', self)
        self.output = QtWidgets.QTextBrowser(self)
        self.user: User = None

        self.threadpool = QThreadPool()
        self.initUI()

    def initUI(self):
        # Create textbox
        self.textbox.move(20, 20)
        self.textbox.resize(360, 40)
        self.textbox.setPlaceholderText("Security name (more than 2 symbols)")

        # Create a button in the window
        self.button.move(400, 20)
        self.button.resize(120, 40)

        # connect button to function on_click
        self.button.clicked.connect(self.find_securities)

        # Create a button in the window
        self.load_all_btn.move(540, 20)
        self.load_all_btn.resize(120, 40)

        # connect button to function on_click
        self.load_all_btn.clicked.connect(self.load_all)

        self.output.setGeometry(QtCore.QRect(10, 10, 680, 360))
        self.output.setObjectName("output")
        self.output.move(20, 80)

    def set_user(self, user):
        self.user = user

    def find_securities(self):
        if len(self.textbox.text()) <= 2:
            return
        GetSecurity(
            StandardQuery(
                SecurityInfo(
                    id=0,
                    figi="",
                    security_name="",
                    ticker="",
                    class_code=""
                ),
                self.textbox.text()
            ),
            self.after_search,
            self.user.get_token(),
            load_coupons=False,
            load_dividends=False,
            load_full_info=False
        ).start()

    def after_search(self, code, data: list[Security]):
        data = [d.get_as_dict() for d in data]
        self.threadpool.start(Worker(data=data, out=self.output))

    def load_all(self):
        LoadAllSecurities(
            self.after_load,
            self.user.get_token()
        ).start()
        self.output.append("Load started")

    def after_load(self, code, data):
        print(code)
        self.threadpool.start(Worker(data=[code], out=self.output))


class Worker(QRunnable):
    """
    Worker thread
    """

    def __init__(self, *args, data=None, out=None, on_finish=None, **kwargs):
        self.on_finish = on_finish
        self.data = data
        self.out = out

        super().__init__(*args, **kwargs)

    @pyqtSlot()
    def run(self):
        """
        Your code goes in this function
        """
        if self.out is not None:
            parsed = [str(i) for i in self.data]
            self.out.append("\n".join(parsed))
        else:
            self.on_finish(self.data)


class CreateWindow:
    login: LoginWindow = None
    reg: RegisterWindow = None
    main_window: Window
    user: User

    WIDTH = 720
    HEIGHT = 480

    def __init__(self, app):
        self.app = app

    def create_main(self):
        screen = self.app.desktop().screenGeometry()

        self.main_window = Window()
        self.main_window.setGeometry((screen.width() - self.WIDTH) // 2,
                                     (screen.height() - self.HEIGHT) // 2,
                                     self.WIDTH, self.HEIGHT)
        self.main_window.setFixedSize(self.WIDTH, self.HEIGHT)

        self.main_window.show()
        self.create_login()

        sys.exit(self.app.exec_())

    def after_enter(self):
        if self.login is not None:
            self.login.deleteLater()
        elif self.reg is not None:
            self.reg.deleteLater()

        self.main_window.set_user(self.user)

    def create_login(self):
        self.login = LoginWindow(self, self.main_window)

        if self.reg is not None:
            self.reg.deleteLater()
            self.reg = None

        self.login.show()

    def create_reg(self):
        self.reg = RegisterWindow(self, self.main_window)

        if self.login is not None:
            self.login.deleteLater()
            self.login = None

        self.reg.show()
