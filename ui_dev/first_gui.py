import os
import sys

from PyQt5.QtGui import QScreen
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox

from api_requests.user_methods import CheckUser, CreateUser
from info.user import User

folder = 'platforms'
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = folder


class LoginWindow(QtWidgets.QDialog):
    loginval: QtWidgets.QLineEdit
    passwordval: QtWidgets.QLineEdit
    newtokenval: QtWidgets.QLineEdit

    layout_main: QtWidgets.QVBoxLayout
    upper_layout: QtWidgets.QVBoxLayout
    lower_layout: QtWidgets.QHBoxLayout

    def __init__(self, on_reg):
        super(LoginWindow, self).__init__()
        self.horizontalGroupBox = None
        self.parent_window: CreateWindow = on_reg
        self.setWindowTitle("SpendYourMoney")
        self.setupLoginUI()

    def setupLoginUI(self):
        self.layout_main = QtWidgets.QVBoxLayout(self)
        self.verticalGroupBox = QtWidgets.QGroupBox("Sign in", self)
        self.layout_main.addWidget(self.verticalGroupBox)

        self.upper_layout = QtWidgets.QVBoxLayout(self.verticalGroupBox)

        self.loginval = QtWidgets.QLineEdit(self)
        self.upper_layout.addWidget(self.loginval)
        self.loginval.setPlaceholderText("login")

        self.passwordval = QtWidgets.QLineEdit(self)
        self.passwordval.setPlaceholderText("password")
        self.passwordval.setEchoMode(QtWidgets.QLineEdit.Password)
        self.upper_layout.addWidget(self.passwordval)

        buttonLogin = QtWidgets.QPushButton("Login", self)
        buttonLogin.clicked.connect(self.handleLogin)
        self.upper_layout.addWidget(buttonLogin)

        self.horizontalGroupBox = QtWidgets.QGroupBox("Registration", self)
        buttonRegisterInstead = QtWidgets.QPushButton("Go to registration",
                                                      self)
        buttonRegisterInstead.clicked.connect(self.parent_window.createReg)
        self.layout_main.addWidget(self.horizontalGroupBox)
        self.lower_layout = QtWidgets.QHBoxLayout(self.horizontalGroupBox)
        self.lower_layout.addWidget(buttonRegisterInstead)

    def createUser(self, code, user):
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

    def handleLogin(self):
        CheckUser(self.loginval.text(), self.passwordval.text(),
                  self.createUser).start()

class RegisterWindow(QtWidgets.QDialog):
    newloginval: QtWidgets.QLineEdit
    newpasswordval: QtWidgets.QLineEdit
    newtokenval: QtWidgets.QLineEdit

    def __init__(self, on_login):
        super(RegisterWindow, self).__init__()
        self.parent_window: CreateWindow = on_login
        self.setWindowTitle("SpendYourMoney")
        self.setupRegisterUI()

    def setupRegisterUI(self):
        layout_main = QtWidgets.QVBoxLayout(self)
        self.verticalGroupBox = QtWidgets.QGroupBox("Registration", self)
        layout_main.addWidget(self.verticalGroupBox)
        layout = QtWidgets.QVBoxLayout(self.verticalGroupBox)
        self.newloginval = QtWidgets.QLineEdit(self)
        self.newloginval.setPlaceholderText("login")
        layout.addWidget(self.newloginval)
        self.newpasswordval = QtWidgets.QLineEdit(self)
        self.newpasswordval.setPlaceholderText("password")
        self.newpasswordval.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.newpasswordval)
        self.newtokenval = QtWidgets.QLineEdit(self)
        self.newtokenval.setPlaceholderText("token")
        layout.addWidget(self.newtokenval)
        buttonRegister = QtWidgets.QPushButton("Register", self)
        buttonRegister.clicked.connect(self.handleRegister)
        layout.addWidget(buttonRegister)

        self.horizontalGroupBox = QtWidgets.QGroupBox("Sign in", self)
        buttonLoginInstead = QtWidgets.QPushButton("Back to login",
                                                   self)
        buttonLoginInstead.clicked.connect(self.parent_window.createLogin)
        layout_main.addWidget(self.horizontalGroupBox)
        layout = QtWidgets.QHBoxLayout(self.horizontalGroupBox)
        layout.addWidget(buttonLoginInstead)


    def afterCreate(self, code: int, loaded_data):
        self.parent_window.user = loaded_data
        if code in (110, 101, 102):
            QMessageBox.warning(self, 'Error', "User already exists")
        elif code == 200:
            self.parent_window.after_enter()
        elif code in (300, 500):
            QMessageBox.warning(self, 'Error', 'Something went wrong')

    def handleRegister(self):
        CreateUser(
            User(
                username=self.newloginval.text(),
                token=self.newtokenval.text()
            ),
            self.newpasswordval.text(),
            self.afterCreate
        ).start()


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


class CreateWindow():
    login: LoginWindow = None
    reg: RegisterWindow = None
    main_window: Window
    user: User

    WIDTH = 500
    HEIGHT = 300

    def __init__(self, app):
        self.app = app

    def createMain(self):
        screen = self.app.desktop().screenGeometry()

        self.main_window = QMainWindow()
        self.main_window.setGeometry((screen.width() - self.WIDTH) // 2,
                                     (screen.height() - self.HEIGHT) // 2,
                                     self.WIDTH, self.HEIGHT)
        self.main_window.setFixedSize(self.WIDTH, self.HEIGHT)
        self.main_window.show()

        self.createLogin()

        sys.exit(self.app.exec_())

    def after_enter(self):
        if self.login is not None:
            self.login.deleteLater()
        elif self.reg is not None:
            self.reg.deleteLater()

    def createLogin(self):
        self.login = LoginWindow(self)

        if self.reg is not None:
            self.reg.destroy(destroyWindow=True)
            self.reg = None

        self.login.show()

    def createReg(self):
        self.reg = RegisterWindow(self)

        if self.login is not None:
            self.login.destroy(destroyWindow=True)
            self.login = None

        self.reg.show()
