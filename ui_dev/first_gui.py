import os
import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton
from PyQt5.QtWidgets import QMessageBox

from api_requests.get_security import GetSecurity
from api_requests.security_getter import StandardQuery
from api_requests.user_methods import CheckUser, CreateUser
from info.user import User
from securities.securities import SecurityInfo

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

    def __init__(self, on_reg):
        super(LoginWindow, self).__init__()
        self.horizontalGroupBox = None
        self.parent_window: CreateWindow = on_reg
        self.setWindowTitle("SpendYourMoney")
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
        button_register_instead.clicked.connect(self.parent_window.create_reg)
        self.layout_main.addWidget(self.horizontalGroupBox)
        self.lower_layout = QtWidgets.QHBoxLayout(self.horizontalGroupBox)
        self.lower_layout.addWidget(button_register_instead)

    def create_user(self, code, user):
        self.parent_window.user = user
        if code in (200, 201, 202, 211):
            self.parent_window.after_enter()
        elif code == 100:
            QMessageBox.warning(self, 'Error', 'Bad user or password')
        elif code == 250:
            QMessageBox.warning(self, 'Error', "User doesn't exists")
        elif code == 300:
            QMessageBox.warning(self, 'Error', 'Something went wrong')
        elif code in (400, 500):
            QMessageBox.warning(self, 'Error', "Invalid token")

    def handle_login(self):
        CheckUser(self.loginval.text(), self.passwordval.text(),
                  self.create_user).start()


class RegisterWindow(QtWidgets.QDialog):
    newloginval: QLineEdit
    newpasswordval: QLineEdit
    newtokenval: QLineEdit

    def __init__(self, on_login):
        super(RegisterWindow, self).__init__()
        self.horizontalGroupBox = QtWidgets.QGroupBox("Sign in", self)
        self.verticalGroupBox = QtWidgets.QGroupBox("Registration", self)
        self.parent_window: CreateWindow = on_login
        self.setWindowTitle("SpendYourMoney")
        self.setup_register_ui()

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
        button_login_instead.clicked.connect(self.parent_window.create_login)
        layout_main.addWidget(self.horizontalGroupBox)
        layout = QtWidgets.QHBoxLayout(self.horizontalGroupBox)
        layout.addWidget(button_login_instead)

    def after_create(self, code: int, loaded_data):
        self.parent_window.user = loaded_data
        if code in (110, 101, 102):
            QMessageBox.warning(self, 'Error', "User already exists")
        elif code == 200:
            self.parent_window.after_enter()
        elif code in (300, 500):
            QMessageBox.warning(self, 'Error', 'Something went wrong')

    def handle_register(self):
        CreateUser(
            User(
                username=self.newloginval.text(),
                token=self.newtokenval.text()
            ),
            self.newpasswordval.text(),
            self.after_create
        ).start()


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.output = QtWidgets.QTextBrowser(self)
        self.user: User = None
        self.initUI()

    def initUI(self):
        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280, 40)
        self.textbox.setPlaceholderText("Security name")

        # Create a button in the window
        self.button = QPushButton('Find security', self)
        self.button.move(340, 20)
        self.button.resize(120, 40)

        # connect button to function on_click
        self.button.clicked.connect(self.find_securities)

        self.output.setGeometry(QtCore.QRect(10, 10, 680, 360))
        self.output.setObjectName("output")
        self.output.move(20, 80)

    def set_user(self, user):
        self.user = user

    def find_securities(self):
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

    def after_search(self, code, data):
        for i in data:
            self.output.append(str(i.get_as_dict()))


class CreateWindow:
    login: LoginWindow = None
    reg: RegisterWindow = None
    main_window: Window
    user: User

    WIDTH = 720
    HEIGHT = 480

    # TODO delete on_finish
    def __init__(self, app):
        self.app = app

    def create_main(self):
        screen = self.app.desktop().screenGeometry()

        self.main_window = Window()
        self.main_window.setGeometry((screen.width() - self.WIDTH) // 2,
                                     (screen.height() - self.HEIGHT) // 2,
                                     self.WIDTH, self.HEIGHT)
        self.main_window.setFixedSize(self.WIDTH, self.HEIGHT)

        self.create_login()
        self.main_window.show()

        sys.exit(self.app.exec_())

    def after_enter(self):
        if self.login is not None:
            self.login.deleteLater()
        elif self.reg is not None:
            self.reg.deleteLater()

        self.main_window.show()
        self.main_window.set_user(self.user)

    def create_login(self):
        self.login = LoginWindow(self)

        if self.reg is not None:
            self.reg.destroy(destroyWindow=True)
            self.reg = None

        self.login.show()

    def create_reg(self):
        self.reg = RegisterWindow(self)

        if self.login is not None:
            self.login.destroy(destroyWindow=True)
            self.login = None

        self.reg.show()
