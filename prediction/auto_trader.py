import datetime
from PyQt5.QtCore import QThread as Thread, pyqtSignal
from tinkoff.invest import CandleInterval

from prediction.rsi import RSI
from securities.securities import SecurityInfo

delta: list = [datetime.timedelta(minutes=1), datetime.timedelta(minutes=5),
               datetime.timedelta(minutes=15), datetime.timedelta(hours=1),
               datetime.timedelta(days=1), datetime.timedelta(minutes=2),
               datetime.timedelta(minutes=3), datetime.timedelta(minutes=10),
               datetime.timedelta(minutes=30), datetime.timedelta(hours=2),
               datetime.timedelta(hours=4), datetime.timedelta(weeks=1)]


class AutoTrader(Thread):
    status_code: int = 200
    info: SecurityInfo
    candle_interval: CandleInterval
    period: int
    end_date: datetime

    def __init__(self, info: SecurityInfo, candle_interval: CandleInterval,
                 token, period: int,
                 end_date: datetime = datetime.datetime.today()):
        super().__init__()
        self.info = info
        self.candle_interval = candle_interval
        self.__token = token
        self.period = period
        self.end_date = end_date

    def run(self) -> None:
        if self.candle_interval.value < 1 or self.candle_interval.value > 12:
            self.status_code = 500
        else:
            rsi_list: list = []
            threads: list[RSI] = []
            for i in range(self.candle_interval):
                threads.append(RSI(  # TODO sdlkhjfsdjkhfjkhsdjkhfkjshdfjkhsjkhdfjkhsjkdhfjkhsdkjfkiughjghjkghjkgjkhghhjkghjkg
                    1,
                    self.__token,
                    self.date_start(self.candle_interval),
                    self.info,
                    lambda x, y: rsi_list.append(y),
                    rsi_step=self.period,
                    candle_interval=i
                ))
                threads[-1].start()

    def date_start(self, candle_interval: CandleInterval):
        start_date: datetime
        if 0 < candle_interval.value < 13:
            start_date = self.end_date - delta[
                candle_interval.value - 1] * self.period * 2 - 1
            return start_date
        else:
            self.status_code = 500  # Incorrect CandleInterval
