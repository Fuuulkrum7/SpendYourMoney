import datetime

from api_requests.get_security_history import GetSecurityHistory
from PyQt5.QtCore import QThread as Thread, pyqtSignal

from securities.securities import SecurityInfo


class RSI(Thread):
    get_sec: GetSecurityHistory
    rsi_step: int
    num_candl: int
    data_downloaded = pyqtSignal(object)

    def __init__(self, set_number_of_candl: int, start_date: datetime, candl_step: int, info: SecurityInfo,
                 on_finish, set_rsi_step: int = 14):
        super().__init__()
        self.rsi_step = set_rsi_step
        self.num_candl = set_number_of_candl
        self.data_downloaded.connect(on_finish)
        # Работа с GetSecurityHistory

    def run(self) -> None:
        self.get_rsi_in_point()

    def get_rsi_in_point(self):
        output: list = []
        target_candl = 1
        while target_candl < self.num_candl:
            up_sum = 0
            up_num = 0
            down_sum = 0
            down_num = 0
            prev_candl = 0
            skiped_candl = 0
            rsi_num = 0
            for candl in self.get_sec.history:
                if skiped_candl < target_candl - 1:
                    skiped_candl += 1
                else:
                    if rsi_num < self.rsi_step:
                        if prev_candl == 0:
                            prev_candl = candl.price
                        else:
                            if prev_candl >= candl.price:
                                down_sum = down_sum + candl.price
                                down_num = down_num + 1
                            else:
                                up_sum = up_sum + candl.price
                                up_num = up_num + 1
                        rsi_num += 1
                    else:
                        break
            output.append(100 - 100 / ((up_sum / up_num) / (down_sum / down_num)))
            target_candl += 1
        self.data_downloaded.emit(output)
