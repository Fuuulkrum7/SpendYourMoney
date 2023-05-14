import datetime
import math

from api_requests.get_security_history import GetSecurityHistory
from PyQt5.QtCore import QThread as Thread, pyqtSignal
from tinkoff.invest import CandleInterval

from securities.securities import SecurityInfo


class BOLLINGER(Thread):
    get_sec: GetSecurityHistory
    period: int
    standard_fl: int
    data_downloaded = pyqtSignal(object)

    def __init__(self, start_date: datetime, info: SecurityInfo,
                 token, on_finish, set_period: int = 20,
                 set_standard_fl: int = 2, candle_interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_DAY):
        super().__init__()
        self.data_downloaded.connect(on_finish)
        self.period = set_period
        self.standard_fl = set_standard_fl
        self.__token = token
        # GetSecurityHistory
        self.to = start_date + self.period
        self.to = self.to.replace(tzinfo=datetime.timezone.utc)

        self.get_sec = GetSecurityHistory(
            info=info,
            _from=start_date,
            to=self.to,
            interval=candle_interval,
            token=self.__token,
            on_finish=1 + 1
        )

        self.get_sec.start()

    def run(self) -> None:
        self.get_bollinger()

    def get_bollinger(self):
        topline: list = []
        midline: list = []
        botline: list = []
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
        self.data_downloaded.emit(topline, midline, botline)
