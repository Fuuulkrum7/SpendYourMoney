import os
import sys
from datetime import timedelta

import PyQt5
from PyQt5 import QtWidgets, QtCore, QtTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton, QListWidget, \
    QTextBrowser, QDialog, QListWidgetItem, QLabel, QWidget
from PyQt5.QtWidgets import QMessageBox
from tinkoff.invest import CandleInterval
from tinkoff.invest.utils import now

from api_requests.get_security import GetSecurity
from api_requests.get_security_history import GetSecurityHistory
from api_requests.load_all_securities import LoadAllSecurities
from api_requests.security_getter import StandardQuery
from api_requests.subscribe_requests import SubscribeOnMarket
from api_requests.user_methods import CheckUser, CreateUser
from info.file_loader import FileLoader
from info.user import User
from neural_network.predictor import PredictCourse
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
            self.check_thread = CheckUser(self.loginval.text(),
                                          self.passwordval.text(),
                                          self.create_user)

            # self.check_thread = CheckUser("admin",
            #                               "admin",
            #                               self.create_user)
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
    predict_thread: PredictCourse = None
    subscribe_thread = None

    figis = []
    data = {}
    idx = 0
    current_sec = None
    res = None
    delta = 0

    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("SpendYourMoney")
        self.textbox = QLineEdit(self)
        self.button = QPushButton('Find security', self)
        self.advanced = QPushButton('Advanced search', self)
        self.figi = QLineEdit(self)
        self.name = QLineEdit(self)
        self.ticker = QLineEdit(self)
        self.classcode = QLineEdit(self)
        self.load_all_btn = QPushButton('Load all', self)
        self.output = QListWidget(self)
        self.user: User = None
        self.isadvanced = False

        self.initUI()

    def initUI(self):
        # Create textbox
        self.textbox.move(20, 20)
        self.textbox.resize(360, 40)
        self.textbox.setPlaceholderText("Security name (more than 2 symbols)")

        # Create a button in the window
        self.button.move(400, 20)
        self.button.resize(120, 40)

        self.advanced.move(540, 20)
        self.advanced.resize(120, 40)

        # connect button to function on_click
        self.button.clicked.connect(self.find_securities)

        self.figi.move(540, 80)
        self.figi.setPlaceholderText('Figi')
        self.figi.setVisible(False)
        self.name.move(540, 120)
        self.name.setPlaceholderText('Security name')
        self.name.setVisible(False)
        self.ticker.move(540, 160)
        self.ticker.setPlaceholderText('Ticker')
        self.ticker.setVisible(False)
        self.classcode.move(540, 200)
        self.classcode.setPlaceholderText('Class code')
        self.classcode.setVisible(False)

        self.advanced.clicked.connect(self.switch_mode)

        # Create a button in the window
        self.load_all_btn.move(680, 20)
        self.load_all_btn.resize(120, 40)

        # connect button to function on_click
        self.load_all_btn.clicked.connect(self.load_all)

        # self.output.setGeometry(QtCore.QRect(10, 10, 680, 360))
        self.output.setObjectName("output")
        self.output.move(20, 80)
        self.output.resize(500, 360)
        self.output.itemClicked.connect(self.security_clicked)

    def security_clicked(self, item):
        self.security = item.data(Qt.UserRole)
        self.security_window = SecurityWindow(self.security, self.user)
        print("1", self.user)
        self.security_window.show()

    def switch_mode(self):
        if self.figi.isVisible():
            self.figi.setVisible(False)
            self.name.setVisible(False)
            self.ticker.setVisible(False)
            self.classcode.setVisible(False)
            self.isadvanced = False
        else:
            self.figi.setVisible(True)
            self.name.setVisible(True)
            self.ticker.setVisible(True)
            self.classcode.setVisible(True)
            self.isadvanced = True

    def set_user(self, user):
        self.user = user

    def find_securities(self):
        # if len(self.textbox.text()) <= 2 or (
        #         self.securities_thread is not None and
        #         self.securities_thread.isRunning()):
        #     return

        # if self.textbox.text() == "start":
        #     self.load_figis()
        #     return

        self.securities_thread = GetSecurity(
            StandardQuery(
                SecurityInfo(
                    figi=self.textbox.text(),
                    security_name=self.textbox.text(),
                    ticker=self.textbox.text(),
                    class_code=self.textbox.text()
                ) if not self.isadvanced else
                SecurityInfo(
                    figi=self.figi.text(),
                    security_name=self.name.text(),
                    ticker=self.ticker.text(),
                    class_code=self.classcode.text()
                )
                ,
                ""
            ),
            self.after_search,
            self.user.get_token(),
            load_coupons=False,
            load_dividends=False,
            load_full_info=False
        )
        self.securities_thread.start()

    def on_predict_made(self, result):
        ...
        # self.output.addItem(str(result[1]))

    def predict_it(self, result):
        code, data = result

        # self.output.addItem(f"Stock name - {data[0].info.name}. "
        #                    f"Prediction: ")

        self.predict_thread = PredictCourse(
            data[0],
            self.on_predict_made,
            self.user.get_token()
        )

        self.predict_thread.start()

    def show_course(self, result):
        ...
        # self.output.addItem(str(result))

    def after_search(self, result):
        code, data = result

        if data:
            self.load_securities(data[0].info)
            if data[0].security_type == SecurityType.STOCK:
                self.securities_thread = GetSecurity(
                    StandardQuery(
                        data[0].info,
                        ""
                    ),
                    self.predict_it,
                    self.user.get_token(),
                    load_dividends=False,
                    load_coupons=False,
                    insert_to_db=False
                )

                self.securities_thread.start()

                # self.subscribe_thread = SubscribeOnMarket(
                #     data[0],
                #     self.user.get_token(),
                #     self.show_course
                # )
                #
                # self.subscribe_thread.start()

        for security in data:
            basic_info = f"Security name={security.info.name}, Figi=" \
                   f"{security.info.figi}, Ticker={security.info.ticker}," \
                   f"Class code={security.info.class_code}"
            basic_info = f"{'*' * len(basic_info)}\n{basic_info}" \
                         f"\n{'*' * len(basic_info)}"
            item = QListWidgetItem(basic_info)
            item.setData(Qt.UserRole, security)
            self.output.addItem(item)

            # data = [d.get_as_dict() for d in data]
            # parsed = [str(i) for i in data]
            # self.output.addItem(parsed)

    def load_all(self):
        if self.all_securities_thread is not None \
                and self.all_securities_thread.isRunning():
            return

        self.all_securities_thread = LoadAllSecurities(
            self.after_load,
            self.user.get_token()
        )
        self.all_securities_thread.start()
        # self.output.addItem("Load started")

    def after_load(self, result):
        code, data = result
        print(code)
        parsed = [str(i) for i in data]
        # self.output.addItem("\n".join(parsed))

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


class CreateWindow:
    login: LoginWindow = None
    reg: RegisterWindow = None
    main_window: Window
    user: User

    WIDTH = 820
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

class SecurityWindow(QMainWindow):
    get_securities_thread: GetSecurity = None
    def __init__(self, item, user):
        super().__init__()
        self.user = user
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle(item.info.figi)
        self.get_securities_thread = GetSecurity(
            StandardQuery(
                item.info,
                ""
            ),
            self.after,
            self.user.get_token()
        )
        self.get_securities_thread.start()

        self.left_name = QLabel("security name:")
        self.right_name = QLabel(item.info.name)
        self.right_lot = QLabel(str(item.lot))
        self.left_currency = QLabel("currency:")
        self.right_currency = QLabel(item.currency)
        self.left_country = QLabel("country:")
        self.right_country = QLabel(item.country)
        self.left_countrycode = QLabel("country code:")
        self.right_countrycode = QLabel(item.country_code)
        self.left_sector = QLabel("sector:")
        self.right_sector = QLabel(item.sector)
        self.left_ticker = QLabel("ticker:")
        self.right_ticker = QLabel(item.info.ticker)
        self.left_classcode = QLabel("class code:")
        self.right_classcode = QLabel(item.info.class_code)

        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QtWidgets.QHBoxLayout()
        widget.setLayout(layout)

        left_widget = QWidget()
        layout.addWidget(left_widget)
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)
        right_widget = QWidget()
        layout.addWidget(right_widget)

        left_vertical = QtWidgets.QVBoxLayout()
        right_vertical = QtWidgets.QVBoxLayout()

        left_widget.setLayout(left_vertical)
        right_widget.setLayout(right_vertical)

        left_vertical.addWidget(self.left_name)
        right_vertical.addWidget(self.right_name)
        # left_vertical.addWidget(self.left_lot)
        # right_vertical.addWidget(self.right_lot)
        left_vertical.addWidget(self.left_currency)
        right_vertical.addWidget(self.right_currency)
        left_vertical.addWidget(self.left_country)
        right_vertical.addWidget(self.right_country)
        left_vertical.addWidget(self.left_countrycode)
        right_vertical.addWidget(self.right_countrycode)
        left_vertical.addWidget(self.left_sector)
        right_vertical.addWidget(self.right_sector)
        left_vertical.addWidget(self.left_ticker)
        right_vertical.addWidget(self.right_ticker)
        left_vertical.addWidget(self.left_classcode)
        right_vertical.addWidget(self.right_classcode)

    def after(self, result):
        code, data = result
        print(data)
        print(data[0].get_as_dict())
        print(data[0].dividend)