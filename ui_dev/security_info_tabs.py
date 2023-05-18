import datetime
import os
from datetime import timedelta
from platform import system

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QTabWidget, \
    QMainWindow, QListWidgetItem, QListWidget, QComboBox, QHBoxLayout
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as \
    FigureCanvas
from matplotlib.figure import Figure
from tinkoff.invest import CandleInterval
from tinkoff.invest.utils import now

from api_requests.get_security import GetSecurity
from api_requests.get_security_history import GetSecurityHistory
from api_requests.security_getter import StandardQuery
from database.database_info import BondsInfo, StocksInfo, SecuritiesInfo, \
    CouponInfo
from info.file_loader import FileLoader
from neural_network.predictor import PredictCourse
from securities.securiries_types import SecurityType
from securities.securities import Security


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class SecurityWindow(QMainWindow):
    get_securities_thread: GetSecurity = None
    get_securities_hist_thread: GetSecurityHistory = None

    WIDTH = 1080
    HEIGHT = 720
    no_result = "Nothing found"
    item: Security = None

    def __init__(self, item, user, settings):
        super().__init__()
        self.predict_thread = None
        self.neural_network = None
        self.right_vertical = None
        self.left_vertical = None
        self.canvas = None
        self.user = user
        self.history = []
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setWindowTitle(item.info.name)

        self.layout = QVBoxLayout(self)
        self.main_widget = QWidget()

        self.item = item

        self.left = []
        self.right = []

        self.tabs = QTabWidget()

        self.security_tab = QWidget()
        self.div_coup_tab = QWidget()
        self.course_tab = QWidget()

        self.tabs.addTab(self.security_tab, "Main info")
        self.tabs.addTab(self.div_coup_tab, "Subdata")
        self.tabs.addTab(self.course_tab, "Course")

        self.divs_and_coupons = QListWidget(self)

        self.settings = settings

        self.candle = CandleInterval(settings["candle"])

        self.init_security_ui()
        self.init_divs_ui()
        self.init_plot_ui()

        self.layout.addWidget(self.tabs)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def init_security_ui(self):
        self.security_tab.layout = QtWidgets.QHBoxLayout()
        self.security_tab.setLayout(self.security_tab.layout)

        left_widget = QWidget()
        self.security_tab.layout.addWidget(left_widget)
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Minimum)
        self.security_tab.layout.addItem(spacer)
        right_widget = QWidget()
        self.security_tab.layout.addWidget(right_widget)

        self.left_vertical = QtWidgets.QVBoxLayout()
        self.right_vertical = QtWidgets.QVBoxLayout()

        left_widget.setLayout(self.left_vertical)
        right_widget.setLayout(self.right_vertical)

        self.get_securities_thread = GetSecurity(
            StandardQuery(
                self.item.info,
                ""
            ),
            self.after,
            self.user.get_token()
        )
        self.get_securities_thread.start()

    def init_divs_ui(self):
        self.div_coup_tab.layout = QtWidgets.QHBoxLayout()
        self.div_coup_tab.setLayout(self.div_coup_tab.layout)

        self.div_coup_tab.layout.addWidget(self.divs_and_coupons)
        self.divs_and_coupons.setObjectName("divs_and_coupons")
        self.divs_and_coupons.move(20, 20)
        self.divs_and_coupons.resize(self.WIDTH - 40, self.HEIGHT - 40)

    def after_divs_load(self, data, flag):
        if not data:
            self.divs_and_coupons.addItem(self.no_result)
            return
        for sub in data:
            sub_dict: dict = sub.get_as_dict()
            sub_dict.pop("security_id")
            sub_dict.pop("ID")

            if flag == SecurityType.BOND:
                sub_dict[CouponInfo.coupon_type.value] = sub.coupon_type

            parsed = ""
            for key, value in sub_dict.items():
                key = key.replace("_", " ") + ": "
                parsed += key + str(value) + "; "
            parsed = parsed[:-2]
            divider = len(parsed) * "*"

            self.divs_and_coupons.addItem(f"{divider}\n{parsed}\n{divider}")

    def init_plot_ui(self):
        self.course_tab.layout = QVBoxLayout()

        self.horizontal = QHBoxLayout()
        self.neural_network = QLabel()
        self.horizontal.addWidget(self.neural_network)
        # self.neural_network.move(200, 5)

        # toolbar = NavigationToolbar2QT(self.canvas, self)

        # self.course_tab.layout.addWidget(toolbar)

        self.select_candle = QComboBox()
        self.horizontal.addWidget(self.select_candle)
        self.course_tab.layout.addLayout(self.horizontal)
        self.canvas = MplCanvas()
        self.course_tab.layout.addWidget(self.canvas)


        self.course_tab.setLayout(self.course_tab.layout)

        self.load_plot()

    def load_plot(self):
        if self.candle == CandleInterval.CANDLE_INTERVAL_1_MIN:
            delta = now() - timedelta(minutes=90)
        elif self.candle == CandleInterval.CANDLE_INTERVAL_5_MIN:
            delta = now() - timedelta(minutes=450)
        elif self.candle == CandleInterval.CANDLE_INTERVAL_15_MIN:
            delta = now() - timedelta(minutes=1350)
        elif self.candle == CandleInterval.CANDLE_INTERVAL_HOUR:
            delta = now() - timedelta(hours=90)
        elif self.candle == CandleInterval.CANDLE_INTERVAL_MONTH:
            delta = datetime.datetime(year=1970, month=1, day=2)
        else:
            delta = now() - timedelta(days=90)

        self.get_securities_hist_thread = GetSecurityHistory(
            info=self.item.info,
            _from=delta,
            to=now(),
            interval=self.candle,
            token=self.user.get_token(),
            on_finish=self.on_load
        )
        self.get_securities_hist_thread.start()

    def after(self, result):
        code, data = result

        item = data[0]

        dict_security: dict = item.get_as_dict_security()
        dict_security.update(item.get_as_dict())

        dict_security.pop(SecuritiesInfo.ID.value)
        dict_security.pop(SecuritiesInfo.PRIORITY.value)

        dict_security[SecuritiesInfo.SECTOR.value] = \
            dict_security[SecuritiesInfo.SECTOR.value].upper()
        dict_security[SecuritiesInfo.SECURITY_TYPE.value] = \
            item.security_type.name.lower()

        if item.security_type == SecurityType.STOCK:
            dict_security[StocksInfo.stock_type.value] = \
                item.stock_type.name.replace("_", " ").lower().capitalize()
            dict_security[StocksInfo.otc_flag.value] = bool(item.otc_flag)
            dict_security[StocksInfo.div_yield_flag.value] = \
                bool(item.div_yield_flag)
        else:
            dict_security[BondsInfo.amortization_flag.value] = \
                bool(item.amortization)
            dict_security[BondsInfo.floating_coupon_flag.value] = \
                bool(item.floating_coupon)
            dict_security[BondsInfo.perpetual_flag.value] = \
                bool(item.perpetual)

        print(dict_security)
        dict_security.pop("security_id")

        for key, value in dict_security.items():
            self.left.append(QLabel(key.replace("_", " ").capitalize()))
            self.right.append(QLabel(str(value)))

        for l, r in zip(self.left, self.right):
            self.left_vertical.addWidget(l)
            self.right_vertical.addWidget(r)

        self.item = item

        self.after_divs_load(item.get_sub_data(), item.security_type)

        if self.item.security_type == SecurityType.STOCK:
            self.predict_thread = PredictCourse(
                self.item,
                self.on_predict_made,
                self.user.get_token()
            )

            self.predict_thread.start()
        else:
            self.neural_network.setText("Not allowed to make a prediction")

    def on_predict_made(self, result):
        code, data = result
        self.neural_network.setText(str(data))

    def on_load(self, result):
        code, data = result

        self.history = data
        dates = [i.info_time for i in self.history]
        prices = [i.price for i in self.history]

        self.canvas.axes.plot(dates, prices)
