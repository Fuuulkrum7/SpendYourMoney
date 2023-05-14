import datetime

from api_requests.get_security_history import GetSecurityHistory
from PyQt5.QtCore import QThread as Thread, pyqtSignal
from tinkoff.invest import CandleInterval

from securities.securities import SecurityInfo


class RSI(Thread):
    get_sec: GetSecurityHistory
    rsi_step: int
    num_candl: int
    data_downloaded = pyqtSignal(object)

    def __init__(self, set_number_of_candl: int, token, start_date: datetime,
                 info: SecurityInfo, on_finish, set_rsi_step: int = 14,
                 candle_interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_DAY):
        super().__init__()
        self.rsi_step = set_rsi_step
        self.num_candl = set_number_of_candl
        self.__token = token
        self.data_downloaded.connect(on_finish)
        # Работа с GetSecurityHistory
        self.to = start_date + self.rsi_step
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
        self.get_rsi_in_point()

    def get_rsi_in_point(self):
        output: list = []
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
            output.append(100 - 100 / ((up_sum / up_num) / (down_sum / down_num)))
            target_candle += 1
        self.data_downloaded.emit(output)
