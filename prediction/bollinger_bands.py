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
    standard_fl: float
    data_downloaded = pyqtSignal(object)
    start_date: datetime
    history: list = []

    def __init__(self, start_date: datetime, info: SecurityInfo,
                 token, end_date: datetime,
                 on_finish, period: int = 90,
                 set_standard_fl: float = 2,
                 candle_interval: CandleInterval
                 = CandleInterval.CANDLE_INTERVAL_DAY):
        super().__init__()
        self.data_downloaded.connect(on_finish)
        self.period = period
        self.standard_fl = set_standard_fl
        self.__token = token
        self.info = info
        self.candle_interval = candle_interval
        self.start_date = start_date - delta[self.candle_interval - 1] * \
                          self.period
        self.to = end_date
        self.to = self.to.replace(tzinfo=datetime.timezone.utc)

    def run(self) -> None:
        self.get_sec = GetSecurityHistory(
            info=self.info,
            _from=self.start_date,
            to=self.to,
            interval=self.candle_interval,
            token=self.__token,
            on_finish=self.on_load
        )
        self.get_sec.start()

        self.get_sec.wait()

        topline: list = []
        midline: list = []
        botline: list = []
        if self.status_code < 300:
            try:
                sum_prices: list = [0] * self.period
                stdev: list = []
                candles: list = []
                for candle in self.get_sec.history:
                    candles.append(candle.price)
                old = self.period
                if int(len(candles)/2) < self.period:
                    self.period = int(len(candles)/2)
                curr = old - self.period
                curr_num = 0
                while curr < old:
                    b = 0
                    while b < self.period:
                        sum_prices[curr] += candles[curr_num + b]
                        b += 1
                    curr += 1
                    curr_num += 1
                print(self.period)
                print(len(candles))
                print(old - self.period)
                print(sum_prices)
                i = 0
                for s_pr in sum_prices:
                    midline.append(s_pr/(len(sum_prices)-(old - self.period)))
                    i += 1
                i = 0
                for ml in midline:
                    if i >= old - self.period:
                        sum_de_pow = 0
                        b = len(candles) - 1
                        while b >= old - self.period:
                            sum_de_pow += math.pow(candles[b] - ml, 2)
                            b -= 1
                        stdev.append(math.sqrt(sum_de_pow /
                                               (len(midline) -
                                                (old - self.period))))
                    i += 1
                i = 0
                for ml in midline:
                    if ml == 0:
                        topline.append(0)
                        botline.append(0)
                    else:
                        topline.append(ml + (self.standard_fl * stdev[i]))
                        botline.append(ml - (self.standard_fl * stdev[i]))
            except Exception as e:
                print(e)
                self.status_code = 500
        print(topline)
        print(midline)
        print(botline)
        self.data_downloaded.emit((self.status_code, [topline,
                                                      midline, botline]))

    def on_load(self, lines):
        code, self.history = lines
        if code == 500 or code == 300:
            self.status_code = 400
