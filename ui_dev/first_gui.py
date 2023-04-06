import os
import sys
from datetime import timedelta

import PyQt5
from PyQt5 import QtWidgets, QtCore, QtTest
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton
from PyQt5.QtWidgets import QMessageBox
from tinkoff.invest import CandleInterval
from tinkoff.invest.utils import now

from api_requests.get_security import GetSecurity
from api_requests.get_security_history import GetSecurityHistory
from api_requests.load_all_securities import LoadAllSecurities
from api_requests.security_getter import StandardQuery
from api_requests.user_methods import CheckUser, CreateUser
from info.file_loader import FileLoader
from info.user import User
from securities.securiries_types import SecurityType
from securities.securities import SecurityInfo

folder = 'platforms'
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = folder


class LoginWindow(QtWidgets.QDialog):
    """
    Класс для выполнения входа в аккаунт или перехода к регистрации
    """
    login_pushed: bool = False

    loginval: QLineEdit
    passwordval: QLineEdit

    check_thread: CheckUser

    layout_main: QtWidgets.QVBoxLayout
    upper_layout: QtWidgets.QVBoxLayout
    lower_layout: QtWidgets.QHBoxLayout

    verticalGroupBox: QtWidgets.QGroupBox

    def __init__(self, on_reg, parent):
        super(LoginWindow, self).__init__(parent)
        self.horizontalGroupBox = None
        self.creater: CreateWindow = on_reg
        self.setWindowTitle("SpendYourMoney")

        self.setWindowFlags(self.windowFlags() | PyQt5.QtCore.Qt.Window)
        self.setWindowModality(PyQt5.QtCore.Qt.WindowModal)

        self.setup_login_ui()

    def setup_login_ui(self):
        """
        Отвечает за настройку виджетов в диалоговом окне
        """
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

    def create_user(self, result):
        """
        Отвечает за вывод сообщений об ошибке
        """
        code, user = result
        self.login_pushed = False
        self.creater.user = user

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

    def handle_login(self):
        """
        Запускает проверку параметров входа
        """
        if not self.login_pushed:
            # self.check_thread = CheckUser(self.loginval.text(),
            #                               self.passwordval.text(),
            #                               self.create_user)

            self.check_thread = CheckUser("admin",
                                          "admin",
                                          self.create_user)
            self.check_thread.start()
            self.login_pushed = True

    def closeEvent(self, evnt):
        """
        Закрытие окна
        """
        evnt.ignore()
        quit(0)


class RegisterWindow(QtWidgets.QDialog):
    """
    Класс для создания аккаунта
    """
    register_pushed = False
    newloginval: QLineEdit
    newpasswordval: QLineEdit
    newtokenval: QLineEdit

    registration_thread: CreateUser

    def __init__(self, on_login, parent):
        super(RegisterWindow, self).__init__(parent)
        self.horizontalGroupBox = QtWidgets.QGroupBox("Sign in", self)
        self.verticalGroupBox = QtWidgets.QGroupBox("Registration", self)
        self.creater: CreateWindow = on_login
        self.setWindowTitle("SpendYourMoney")
        self.setup_register_ui()

        self.setWindowFlags(self.windowFlags() | PyQt5.QtCore.Qt.Window)
        self.setParent(parent)
        self.setWindowModality(PyQt5.QtCore.Qt.WindowModal)

    def setup_register_ui(self):
        """
        Отвечает за настройку виджетов в диалоговом окне
        """
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

    def after_create(self, result):
        """
        Отвечает за вывод сообщений об ошибке
        """
        code, loaded_data = result

        self.register_pushed = False
        self.creater.user = loaded_data

        if code in (110, 101, 102):
            QMessageBox.warning(self, 'Error', "User already exists")
        elif code == 200:
            self.creater.after_enter()
        elif code in (300, 500):
            QMessageBox.warning(self, 'Error', 'Something went wrong')

    def handle_register(self):
        """
        Отвечает за создание пользователя в бд
        """
        if not self.register_pushed:
            self.registration_thread = CreateUser(
                User(
                    username=self.newloginval.text(),
                    token=self.newtokenval.text()
                ),
                self.newpasswordval.text(),
                self.after_create
            )

            self.registration_thread.start()
            self.register_pushed = True

    def closeEvent(self, evnt):
        """
        Закрытие окна
        """
        evnt.ignore()
        quit(0)


class Window(QMainWindow):
    """
    Класс для поиска цб
    """
    securities_thread: GetSecurity = None
    all_securities_thread: LoadAllSecurities = None

    figis = []
    data = {}
    idx = 0
    current_sec = None
    res = None
    delta = 0

    def __init__(self):
        super(Window, self).__init__()
        self.textbox = QLineEdit(self)
        self.button = QPushButton('Find security', self)
        self.load_all_btn = QPushButton('Load all', self)
        self.output = QtWidgets.QTextBrowser(self)
        self.user: User = None

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
        if len(self.textbox.text()) <= 2 or (
                self.securities_thread is not None and
                self.securities_thread.isRunning()):
            return

        # if self.textbox.text() == "start":
        #     self.load_figis()
        #     return

        self.securities_thread = GetSecurity(
            StandardQuery(
                SecurityInfo(
                    id=0,
                    figi=self.textbox.text(),
                    security_name=self.textbox.text(),
                    ticker=self.textbox.text(),
                    class_code=self.textbox.text()
                ),
                ""
            ),
            self.after_search,
            self.user.get_token(),
            load_coupons=False,
            load_dividends=False,
            load_full_info=False
        )
        self.securities_thread.start()

    # def load_figis(self):
    #     with open("figis.txt") as f:
    #         a = f.read().split("\n")
    #         a.pop()
    #
    #         self.figis = a
    #         self.idx = 0
    #
    #         f.close()
    #
    #     key = 0
    #     self.data = FileLoader.get_json("parsed_data.json")
    #     if self.data is None:
    #         self.data = {}
    #     else:
    #         key = list(self.data.keys())[-1]
    #         key = self.figis.index(key)
    #         print(key)
    #         if len(self.figis) - key < 100:
    #             self.output.append("load is finishing")
    #
    #     self.figis = self.figis[key: key + 101]
    #
    #     self.load_sec()

    def after_search(self, result):
        code, data = result

        if data:
            self.load_securities(data[0].info)
        data = [d.get_as_dict() for d in data]
        parsed = [str(i) for i in data]
        self.output.append("\n".join(parsed))

    def load_all(self):
        if self.all_securities_thread is not None \
                and self.all_securities_thread.isRunning():
            return

        self.all_securities_thread = LoadAllSecurities(
            self.after_load,
            self.user.get_token()
        )
        self.all_securities_thread.start()
        self.output.append("Load started")

    def after_load(self, result):
        code, data = result
        print(code)
        parsed = [str(i) for i in data]
        self.output.append("\n".join(parsed))

    def load_securities(self, info):
        self.res = GetSecurityHistory(
            info=info,
            _from=now() - timedelta(days=1000),
            to=now(),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
            token=self.user.get_token(),
            on_finish=self.on_load
        )

        self.res.start()

    def on_load(self, data):
        x, y = data
        print(
            len(y),
            sep='\n'
        )

    # def after_histr_load(self, data):
    #     x, y = data
    #
    #     for_load = []
    #     for i in y:
    #         for_load.append(i.get_as_dict())
    #         for_load[-1].pop("security_id")
    #         for_load[-1]["info_time"] = str(for_load[-1]["info_time"])
    #
    #     self.data[self.current_sec.info.figi]["history"] = for_load
    #
    #     self.load_sec()
    #
    # def load_histr(self, data):
    #     code, sec = data
    #
    #     if len(sec) and sec[0].security_type == SecurityType.STOCK:
    #         self.current_sec = sec[0]
    #         sec.clear()
    #
    #         sec = self.current_sec.get_as_dict_security()
    #         sec.update(self.current_sec.get_as_dict())
    #
    #         sec.pop('country')
    #         sec.pop('security_type')
    #         sec.pop('ID')
    #         sec.pop('security_id')
    #         sec.pop('figi')
    #         sec["ipo_date"] = str(sec["ipo_date"])
    #
    #         for_load = []
    #
    #         sec['history'] = for_load
    #
    #         self.data[self.current_sec.info.figi] = sec
    #
    #         self.res = GetSecurityHistory(
    #             info=self.current_sec.info,
    #             _from=now() - timedelta(days=1001),
    #             to=now() - timedelta(days=1),
    #             interval=CandleInterval.CANDLE_INTERVAL_DAY,
    #             token=self.user.get_token(),
    #             on_finish=self.after_histr_load
    #         )
    #
    #         self.res.start()
    #     else:
    #         self.load_sec()
    #
    # def load_sec(self):
    #     if self.idx < len(self.figis):
    #         self.securities_thread = GetSecurity(
    #             StandardQuery(
    #                 SecurityInfo(
    #                     id=0,
    #                     figi=self.figis[self.idx],
    #                 ),
    #                 ""
    #             ),
    #             self.load_histr,
    #             self.user.get_token(),
    #             load_coupons=False,
    #             load_dividends=False,
    #             insert_to_db=False
    #         )
    #         print(self.figis[self.idx])
    #         self.idx += 1
    #
    #         self.securities_thread.start()
    #     else:
    #         print("finish")
    #         FileLoader.save_json(f"parsed_data.json", self.data)


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
