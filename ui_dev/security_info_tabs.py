from datetime import timedelta

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QTabWidget, \
    QMainWindow
from PyQt5.uic.properties import QtWidgets
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as \
    FigureCanvas
from matplotlib.figure import Figure
from tinkoff.invest import CandleInterval
from tinkoff.invest.utils import now

from api_requests.get_security import GetSecurity
from api_requests.get_security_history import GetSecurityHistory
from api_requests.security_getter import StandardQuery
from database.database_info import BondsInfo, StocksInfo, SecuritiesInfo
from securities.securiries_types import SecurityType


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class SecurityWindow(QMainWindow):
    get_securities_thread: GetSecurity = None
    get_securities_hist_thread: GetSecurityHistory = None

    def __init__(self, item, user):
        super().__init__()
        self.canvas = None
        self.user = user
        self.history = []
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle(item.info.name)

        self.layout = QVBoxLayout(self)
        self.main_widget = QWidget()

        self.get_securities_thread = GetSecurity(
            StandardQuery(
                item.info,
                ""
            ),
            self.after,
            self.user.get_token()
        )
        self.get_securities_thread.start()

        self.get_securities_hist_thread = GetSecurityHistory(
            info=self.stock.info,
            _from=now() - timedelta(days=1001),
            to=self.to,
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
            token=self.__token,
            on_finish=self.on_load
        )

        self.left = []
        self.right = []

        self.tabs = QTabWidget()

        self.security_tab = QWidget()
        self.div_coup_tab = QWidget()
        self.course_tab = QWidget()

        self.tabs.addTab(self.security_tab, "Tab 1")
        self.tabs.addTab(self.div_coup_tab, "Tab 2")
        self.tabs.addTab(self.course_tab, "Tab 3")

        self.init_security_ui()
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

    def init_plot_ui(self):
        self.canvas = MplCanvas()

        toolbar = NavigationToolbar2QT(self.canvas, self)

        self.course_tab.layout = QVBoxLayout()
        self.course_tab.layout.addWidget(toolbar)
        self.course_tab.layout.addWidget(self.canvas)
        self.course_tab.setLayout(self.course_tab.layout)

    def after(self, result):
        code, data = result

        item = data[0]

        dict_security: dict = item.get_as_dict_security()
        dict_security.update(item.get_as_dict())

        dict_security.pop(SecuritiesInfo.ID.value)

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

    def on_load(self, result):
        code, data = result

        self.history = data
        self.dates = [i.info_time for i in self.history]
        self.prices = [i.price for i in self.history]

        self.canvas.axes.plot_date(self.dates, self.prices)
