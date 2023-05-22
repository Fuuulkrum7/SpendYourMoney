import datetime
import math

from api_requests.get_security_history import GetSecurityHistory
from PyQt5.QtCore import QThread as Thread, pyqtSignal
from tinkoff.invest import CandleInterval

from securities.securities import SecurityInfo

delta: list = [datetime.timedelta(minutes=1), datetime.timedelta(minutes=5),
               datetime.timedelta(minutes=15), datetime.timedelta(hours=1),
               datetime.timedelta(days=1), datetime.timedelta(minutes=2),
               datetime.timedelta(minutes=3), datetime.timedelta(minutes=10),
               datetime.timedelta(minutes=30), datetime.timedelta(hours=2),
               datetime.timedelta(hours=4), datetime.timedelta(weeks=1)]

class Bollinger(Thread):
    status_code: int = 200
    get_sec: GetSecurityHistory
    period: int
    info: SecurityInfo
    candle_interval: CandleInterval
    standard_fl: int
    data_downloaded = pyqtSignal(object)
    start_date: datetime

    def __init__(self, start_date: datetime, info: SecurityInfo,
                 token, on_finish, period: int = 20,
                 set_standard_fl: int = 2, candle_interval: CandleInterval
                 = CandleInterval.CANDLE_INTERVAL_DAY):
        super().__init__()
        self.data_downloaded.connect(on_finish)
        self.period = period
        self.standard_fl = set_standard_fl
        self.__token = token
        self.info = info
        self.candle_interval = candle_interval
        self.start_date = start_date
        self.to = self.start_date + delta[
                candle_interval.value - 1]*self.period * 2 - 1
        self.to = self.to.replace(tzinfo=datetime.timezone.utc)

    def run(self) -> None:
        self.load_history()
        self.get_sec.wait()
        self.get_bollinger()

    def get_bollinger(self):
        topline: list = []
        midline: list = []
        botline: list = []
        if self.status_code < 300:
            try:
                sum_prices: list = []
                prices: list = []
                stdev: list = []
                i = 0
                while i < self.period:
                    sum_prices.append(0)
                i = 0
                for candle in self.get_sec.history:
                    b = i - self.period + 1
                    if b < 0:
                        b = 0
                    while b <= i:
                        sum_prices[b] += candle.price
                        b += 1
                    i += 1
                    prices.append(candle.price)
                for price in sum_prices:
                    midline.append(price / self.period)
                i = 0
                for ml in midline:
                    sum_de_pow = 0
                    b = i
                    while b < i + self.period:
                        sum_de_pow += math.pow(prices[b] - ml, 2)
                    stdev.append(math.sqrt(sum_de_pow / self.period))
                    i += 1
                i = 0
                for ml in midline:
                    topline.append(ml + (self.standard_fl * stdev[i]))
                    botline.append(ml - (self.standard_fl * stdev[i]))
                    i += 1
            except Exception as e:
                print(e)
                self.status_code = 500

        self.data_downloaded.emit((self.status_code, topline,
                                   midline, botline))

    def on_load(self, topline, midline, botline):
        code, top = topline, mid = midline, bot = botline

        if code == 500 or code == 300:
            self.status_code = 400
            return

        if len(top) < self.period or len(mid) < self.period:
            self.status_code = 300

    def load_history(self):
        self.get_sec = GetSecurityHistory(
            info=self.info,
            _from=self.start_date,
            to=self.to,
            interval=self.candle_interval,
            token=self.__token,
            on_finish=self.on_load
        )
        self.get_sec.start()
