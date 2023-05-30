"""
Модуль с классом окна ЦБ
"""
import datetime
from datetime import timedelta

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QTabWidget, \
    QMainWindow, QListWidget, QComboBox, QHBoxLayout, \
    QMessageBox, QCheckBox, QScrollArea
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as \
    FigureCanvas
import matplotlib as plt
from matplotlib.figure import Figure
from tinkoff.invest import CandleInterval
from tinkoff.invest.utils import now

from api_requests.get_security import GetSecurity
from api_requests.get_security_history import GetSecurityHistory
from api_requests.security_getter import StandardQuery
from api_requests.subscribe_requests import SubscribeOnMarket
from database.database_info import BondsInfo, StocksInfo, SecuritiesInfo, \
    CouponInfo
from info.file_loader import FileLoader
from info.user import User
from neural_network.predictor import PredictCourse
from prediction.bollinger_bands import Bollinger
from prediction.rsi import RSI
from securities.securiries_types import SecurityType
from securities.securities import Security
from ui_dev.loading import LoadingDialog

plt.use("Qt5Agg")

candles_dict = {
    "1 minute": CandleInterval.CANDLE_INTERVAL_1_MIN,
    "5 minute": CandleInterval.CANDLE_INTERVAL_5_MIN,
    "15 Minutes": CandleInterval.CANDLE_INTERVAL_15_MIN,
    "1 hour": CandleInterval.CANDLE_INTERVAL_HOUR,
    "1 day": CandleInterval.CANDLE_INTERVAL_DAY,
    "1 week": CandleInterval.CANDLE_INTERVAL_WEEK,
    "Whole history": CandleInterval.CANDLE_INTERVAL_MONTH
}


class MplCanvas(FigureCanvas):
    """
    Создание холста для графика
    """
    def __init__(self, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class SecurityWindow(QMainWindow):
    """
    Класс отображения всей информации по одной ЦБ
    """
    get_securities_thread: GetSecurity = None
    get_securities_hist_thread: GetSecurityHistory = None

    WIDTH = 1000
    HEIGHT = 700
    no_result = "Nothing found"
    item: Security = None
    just_created = 0
    loading = None

    def __init__(self, item: Security, user: User, settings: dict, path):
        super().__init__()

        self.canvas_layout = None
        self.canvas_widget = None
        self.scroll_area = None
        self.canvas2 = None
        self.rsi_thread = None
        self.bollinger_box = None
        self.rsi_box = None
        self.bollinger_thread = None
        self.__path = path
        self.select_candle = None
        self.horizontal = None
        self.predict_thread = None
        self.subscribe_thread = None
        self.right_vertical = None
        self.left_vertical = None
        self.neural_layout = None
        self.canvas = None
        self.user = user
        self.history = []

        screen = QtWidgets.QDesktopWidget().screenGeometry(-1)

        if screen.height() > 900:
            self.HEIGHT = 860
            self.WIDTH = 1200

        self.setGeometry((screen.width() - self.WIDTH) // 2,
                         (screen.height() - self.HEIGHT) // 2,
                         self.WIDTH, self.HEIGHT)
        # self.setFixedSize(self.WIDTH, self.HEIGHT)
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

        if 0 <= settings["candle"] <= 5 or settings["candle"] in \
                [CandleInterval.CANDLE_INTERVAL_MONTH.value,
                 CandleInterval.CANDLE_INTERVAL_WEEK.value]:
            self.candle = CandleInterval(settings["candle"])
        else:
            self.candle = CandleInterval.CANDLE_INTERVAL_DAY

        self.init_security_ui()
        self.init_divs_ui()
        self.init_plot_ui()

        self.tabs.tabBarClicked.connect(self.tab_changed)

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
            self.on_security_load,
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
        """
        Отображение дивидендов/купонов
        """
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

    def tab_changed(self, index):
        """
        Обработка смены вкладки
        """
        if index == 2 and self.just_created == 1:
            self.just_created = 2

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)

            msg.setText("Data to display not found")
            msg.setWindowTitle("Critical MessageBox")
            msg.setStandardButtons(QMessageBox.Ok)

            msg.exec_()

    def init_plot_ui(self):
        self.course_tab.layout = QVBoxLayout()

        self.horizontal = QHBoxLayout()
        self.neural_layout = QVBoxLayout()
        self.horizontal.addLayout(self.neural_layout)

        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Minimum)
        self.horizontal.addItem(spacer)

        self.rsi_box = QCheckBox("RSI")
        self.bollinger_box = QCheckBox("Bollinger")

        self.rsi_box.stateChanged.connect(self.rsi_changed)
        self.bollinger_box.stateChanged.connect(self.bollinger_changed)

        self.select_candle = QComboBox()
        self.select_candle.resize(80, 40)
        self.select_candle.addItems(list(candles_dict.keys()))
        self.select_candle.setCurrentIndex(list(candles_dict.values()).index(
            self.candle
        ))
        self.select_candle.currentIndexChanged.connect(self.on_candle_change)

        self.horizontal.addWidget(self.rsi_box)
        self.horizontal.addWidget(self.bollinger_box)
        self.horizontal.addWidget(self.select_candle)
        self.course_tab.layout.addLayout(self.horizontal)

        self.canvas = MplCanvas()
        toolbar = NavigationToolbar2QT(self.canvas, self)

        self.canvas.setFixedSize(self.WIDTH - 70, 640)

        self.scroll_area = QScrollArea()

        self.canvas_widget = QWidget()
        self.canvas_layout = QVBoxLayout()

        self.canvas_layout.addWidget(toolbar)
        self.canvas_layout.addWidget(self.canvas)

        self.canvas2 = MplCanvas()
        self.canvas2.setFixedSize(self.WIDTH - 70, 320)
        self.canvas2.setVisible(False)
        self.canvas_layout.addWidget(self.canvas2)

        self.canvas_widget.setLayout(self.canvas_layout)
        self.scroll_area.setWidget(self.canvas_widget)

        self.scroll_area.setWidgetResizable(True)
        self.course_tab.layout.addWidget(self.scroll_area)

        self.course_tab.setLayout(self.course_tab.layout)

        self.check_subscription()

        self.loading = LoadingDialog()
        self.loading.start_loading()
        self.load_plot()

    def add_rsi_canvas(self):
        """
        Отображение RSI графика
        """
        if self.candle != CandleInterval.CANDLE_INTERVAL_MONTH:
            self.canvas2.setVisible(True)
            QTimer.singleShot(0, self.update_scroll_size)

    def delete_rsi_canvas(self):
        """
        Скрытие RSI графика
        """
        if self.candle != CandleInterval.CANDLE_INTERVAL_MONTH:
            self.canvas2.setVisible(False)
            QTimer.singleShot(0, self.update_scroll_size)

    def on_subscribe_update(self, data):
        """
        Обновление по подписке на ЦБ
        """
        print("data check", data)
        if self.candle != CandleInterval.CANDLE_INTERVAL_1_MIN:
            self.subscribe_thread.stop()
            return
        code, new_candle = data
        if new_candle is None or new_candle == self.history[-1]:
            return

        if new_candle.info_time != self.history[-1].info_time:
            self.history.pop(0)
            self.history.append(new_candle)
        else:
            self.history[-1] = new_candle
        self.draw_plot()
        self.bollinger_changed()
        self.rsi_changed()

    def check_subscription(self):
        """
        Включение/выключение подписки
        """
        if self.subscribe_thread is not None:
            self.subscribe_thread.stop()
            print("subscribtion stopped")
        if self.candle == CandleInterval.CANDLE_INTERVAL_1_MIN:
            self.subscribe_thread = SubscribeOnMarket(
                self.item.info,
                self.user.get_token(),
                self.on_subscribe_update
            )

            self.subscribe_thread.start()
            print("subscription started")

    def on_candle_change(self, val):
        """
        Обработка смены свечи
        """
        self.candle = list(candles_dict.values())[val]

        self.check_subscription()

        self.loading = LoadingDialog()
        self.loading.start_loading()

        self.load_plot()

    def calculate_delta(self):
        coef = 2
        if self.candle == CandleInterval.CANDLE_INTERVAL_1_MIN:
            return now() - timedelta(minutes=90 * coef)
        if self.candle == CandleInterval.CANDLE_INTERVAL_5_MIN:
            return now() - timedelta(minutes=450 * coef)
        if self.candle == CandleInterval.CANDLE_INTERVAL_15_MIN:
            return now() - timedelta(minutes=1350 * coef)
        if self.candle == CandleInterval.CANDLE_INTERVAL_HOUR:
            return now() - timedelta(hours=90 * coef)
        if self.candle == CandleInterval.CANDLE_INTERVAL_WEEK:
            return now() - timedelta(days=630 * coef)
        if self.candle == CandleInterval.CANDLE_INTERVAL_MONTH:
            return datetime.datetime(year=1970, month=1, day=2)
        return now() - timedelta(days=90 * coef)

    def load_plot(self):
        """
        Загрузка данных для графика
        """
        self.rsi_box.setEnabled(False)
        self.bollinger_box.setEnabled(False)

        self.get_securities_hist_thread = GetSecurityHistory(
            info=self.item.info,
            _from=self.calculate_delta(),
            to=now(),
            interval=self.candle,
            token=self.user.get_token(),
            on_finish=self.on_history_load
        )
        self.get_securities_hist_thread.start()

    def on_security_load(self, result):
        """
        Загрузка полной информации о ЦБ
        """
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

        dict_security.pop("security_id")

        for key, value in dict_security.items():
            self.left.append(QLabel(key.replace("_", " ").capitalize()))
            self.right.append(QLabel(str(value)))

        for le, r in zip(self.left, self.right):
            self.left_vertical.addWidget(le)
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
            label1 = QLabel("Not allowed to make a prediction")
            self.neural_layout.addWidget(label1)

    def on_predict_made(self, result):
        """
        Отображение предсказания нейросети
        """
        code, data = result
        if data:
            s = sum(data)

            # Такой перевод данных в строку нужен для их корректного
            # отображения
            label1 = QLabel(f'Growth probability: {str(data[2])} %')
            label2 = QLabel(f'Flat probability: {str(data[1])} %')
            label3 = QLabel(f'Fall probability: {str(data[0])} %')

            if s >= 110:
                label1.setStyleSheet("color: cyan")
                label2.setStyleSheet("color: cyan")
                label3.setStyleSheet("color: cyan")
            elif s <= 90:
                label1.setStyleSheet("color: red")
                label2.setStyleSheet("color: red")
                label3.setStyleSheet("color: red")
            self.neural_layout.addWidget(label1)
            self.neural_layout.addWidget(label2)
            self.neural_layout.addWidget(label3)
        else:
            label1 = QLabel("No data")
            self.neural_layout.addWidget(label1)

    def draw_plot(self):
        """
        Построение графика
        """
        if self.canvas:
            self.canvas.axes.clear()

        if len(self.history) > 1:
            dates = [i.info_time for i in self.history]
            prices = [i.price for i in self.history]

            self.canvas.axes.plot(dates, prices)
            self.canvas.axes.plot(dates, [max(prices)] * len(dates), 'g',
                                  linestyle='dashed')
            self.canvas.axes.plot(dates, [min(prices)] * len(dates), 'y',
                                  linestyle='dashed')
            self.canvas.axes.plot(dates, [prices[-1]] * len(dates), 'c',
                                  linestyle='dashed')

            self.canvas.axes.text(dates[-1], prices[-1], str(prices[-1]))
            self.canvas.axes.text(dates[-1], max(prices), str(max(prices)))
            self.canvas.axes.text(dates[-1], min(prices), str(min(prices)))

            self.canvas.axes.margins(x=0)

        self.canvas.draw()

    def on_history_load(self, result):
        """
        Завершение полной загрузки ЦБ
        """
        code, data = result

        self.save_settings()

        if self.candle != CandleInterval.CANDLE_INTERVAL_MONTH:
            self.history = data[max(len(data) - 90, 0):]
        else:
            self.history = data

        print("history len", len(self.history))
        cleared = self.just_created
        self.just_created = 2 if len(self.history) > 1 else 1

        self.draw_plot()
        self.loading.after_load()

        if cleared:
            self.tab_changed(2)

        self.rsi_box.setEnabled(True)
        self.bollinger_box.setEnabled(True)
        self.bollinger_changed()
        self.rsi_changed()

    def update_scroll_size(self):
        """
        Настройка размера прокрутки
        """
        left, top, right, bottom = self.canvas_layout.getContentsMargins()
        hint = self.canvas_layout.sizeHint()
        self.scroll_area.setMaximumHeight(hint.height() + top + bottom + 1)

    def rsi_changed(self):
        """
        Включение/выключение RSI
        """
        if self.rsi_box.isChecked() and \
                self.candle != CandleInterval.CANDLE_INTERVAL_MONTH and \
                (self.rsi_thread is None or not self.rsi_thread.isRunning()):
            self.rsi_thread = RSI(
                len(self.history),
                self.user.get_token(),
                self.calculate_delta(),
                now(),
                self.item.info,
                self.show_rsi,
                candle_interval=self.candle
            )

            self.rsi_thread.start()
            self.canvas.setFixedSize(self.WIDTH - 70, 540)
            self.add_rsi_canvas()
        elif not self.rsi_box.isChecked() and \
                (self.rsi_thread is None or not self.rsi_thread.isRunning()):
            self.canvas.setFixedSize(self.WIDTH - 70, 640)
            self.delete_rsi_canvas()

    def show_rsi(self, result):
        if self.candle == CandleInterval.CANDLE_INTERVAL_MONTH:
            return
        """
        Построение RSI
        """
        code, data = result
        print("rsi len", len(data))

        self.canvas2.axes.clear()
        info_time = [
                        i.info_time for i in self.history
                     ][max(len(self.history) - len(data), 0):]
        
        self.canvas2.axes.plot(
            info_time, data
        )
        self.canvas2.axes.plot(
            info_time,
            [70] * len(data),
            'c',
            linestyle='dashed'
        )
        self.canvas2.axes.plot(
            info_time,
            [30] * len(data),
            'r',
            linestyle='dashed'
        )
        self.canvas2.axes.margins(x=0)

        self.canvas2.draw()

    def bollinger_changed(self):
        """
        Включение/выключение боллинджера
        """
        if self.bollinger_box.isChecked() and \
                self.candle != CandleInterval.CANDLE_INTERVAL_MONTH \
                and (self.bollinger_thread is None
                     or not self.bollinger_thread.isRunning()):
            print("start bollinger")

            self.bollinger_thread = Bollinger(
                self.calculate_delta(),
                self.item.info,
                self.user.get_token(),
                now(),
                self.show_bollinger,
                period=len(self.history),
                candle_interval=self.candle,
                set_standard_fl=0.5
            )

            self.bollinger_thread.start()
        elif self.candle != CandleInterval.CANDLE_INTERVAL_MONTH:
            self.draw_plot()

    def show_bollinger(self, result):
        """
        Отображение линий боллинджера
        """
        if not self.bollinger_box.isChecked():
            return
        code, data = result
        print("bollinger finished")
        print("bollinger len", len(data[0]))

        dates = [i.info_time for i in self.history]
        for i in data:
            if i:
                self.canvas.axes.plot(dates, i, 'r')
        self.canvas.draw()

    def save_settings(self):
        """
        Сохранение настроек
        """
        self.settings["candle"] = self.candle.value

        FileLoader.save_json(
            self.__path + "/info/files/.current_settings.json",
            self.settings
        )
