import datetime

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
        if self.status_code < 300:
            try:
                target_candle = 1
                while target_candle < self.num_candl:
                    up_sum = 0
                    up_num = 0
                    down_sum = 0
                    down_num = 0
                    prev_candle = 0
                    skiped_candle = 0
                    rsi_num = 0
                    for candle in self.get_sec.history:
                        if skiped_candle < target_candle - 1:
                            skiped_candle += 1
                        else:
                            if rsi_num < self.rsi_step:
                                if prev_candle == 0:
                                    prev_candle = candle.price
                                else:
                                    if prev_candle >= candle.price:
                                        down_sum = down_sum + candle.price
                                        down_num = down_num + 1
                                    else:
                                        up_sum = up_sum + candle.price
                                        up_num = up_num + 1
                                rsi_num += 1
                            else:
                                break
                    output.append(100 - 100 / ((up_sum / up_num)
                                               / (down_sum / down_num)))
                    target_candle += 1
            except Exception as e:
                print(e)
                self.status_code = 500
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
