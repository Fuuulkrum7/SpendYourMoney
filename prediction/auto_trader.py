import datetime
from PyQt5.QtCore import QThread as Thread, pyqtSignal
from tinkoff.invest import CandleInterval

from securities.securities import SecurityInfo

delta: list = [datetime.timedelta(minutes=1), datetime.timedelta(minutes=2), datetime.timedelta(minutes=3),
               datetime.timedelta(minutes=5), datetime.timedelta(minutes=10), datetime.timedelta(minutes=15),
               datetime.timedelta(minutes=30), datetime.timedelta(hours=1), datetime.timedelta(hours=2),
               datetime.timedelta(hours=4), datetime.timedelta(days=1), datetime.timedelta(weeks=1)]


class AutoTrader(Thread):
    status_code: int = 200
    info: SecurityInfo
    candle_interval: CandleInterval
    period: int
    start_date: datetime
    end_date: datetime

    def __init__(self, info: SecurityInfo, candl_interval: CandleInterval, token, period: int,
                 end_date: datetime = datetime.datetime.today()):
        super().__init__()
        self.info = info
        self.candle_interval = candl_interval
        self.__token = token
        self.period = period
        self.end_date = end_date
        if 0 <= candl_interval.value - 1 < 12:
            self.start_date = end_date - delta[candl_interval.value - 1] * period
        else:
            self.status_code = 500  # Incorrect CandleInterval
