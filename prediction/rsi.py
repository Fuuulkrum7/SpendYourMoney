import datetime
import modulefinder

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


class RSI(Thread):
    status_code: int = 200
    get_sec: GetSecurityHistory
    rsi_step: int
    num_candl: int
    start_date: datetime
    info: SecurityInfo
    candle_interval: CandleInterval
    data_downloaded = pyqtSignal(object)

    def __init__(self, num_candl: int, token, start_date: datetime,
                 end_date: datetime, info: SecurityInfo, on_finish,
                 rsi_step: int = 14,
                 candle_interval: CandleInterval =
                 CandleInterval.CANDLE_INTERVAL_DAY):
        super().__init__()
        self.rsi_step = rsi_step
        self.num_candl = num_candl
        self.__token = token
        self.data_downloaded.connect(on_finish)
        self.info = info
        self.candle_interval = candle_interval
        self.start_date = start_date
        self.to = end_date
        self.to = self.to.replace(tzinfo=datetime.timezone.utc)

    def run(self) -> None:
        self.load_history()
        self.get_sec.wait()
        self.get_rsi_in_point()

    def get_rsi_in_point(self):
        output: list = []
        if len(self.get_sec.history) - self.rsi_step < self.num_candl:
            self.num_candl = len(self.get_sec.history) - self.rsi_step
        if self.status_code < 300:
            try:
                target_candle = 0
                while target_candle < self.num_candl:
                    gain: list = []
                    lost: list = []
                    prev_candle = 0
                    skipped_candle = 0
                    rsi_num = 0
                    for candle in self.get_sec.history:
                        if skipped_candle < target_candle:
                            skipped_candle += 1
                        else:
                            if rsi_num < self.rsi_step:
                                if prev_candle == 0:
                                    prev_candle = candle.price
                                else:
                                    val = ((candle.price / prev_candle) - 1) \
                                          * 100
                                    if val > 0:
                                        gain.append(val)
                                        lost.append(0)
                                    else:
                                        lost.append(-val)
                                        gain.append(0)
                                    prev_candle = candle.price
                                rsi_num += 1
                            else:
                                break
                    if sum(gain) == 0:
                        gain.append(1)
                    if sum(lost) == 0:
                        lost.append(1)
                    output.append((100 / (1 +
                                          ((sum(gain) / len(gain))
                                           / (sum(lost) / len(lost))))))
                    target_candle += 1
            except Exception as e:
                self.status_code = 500
            print(self.num_candl)
            print(len(output))
        self.data_downloaded.emit((self.status_code, output))

    def on_load(self, output):
        code, result = output

        if code == 500 or code == 300:
            self.status_code = 400
            return

        if len(result) < self.rsi_step:
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
