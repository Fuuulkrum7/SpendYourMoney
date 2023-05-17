import datetime
from PyQt5.QtCore import QThread as Thread, pyqtSignal
from tinkoff.invest import CandleInterval

from securities.securities import SecurityInfo


class AutoTrader(Thread):
    status_code: int = 200
    info: SecurityInfo
    candle_interval: CandleInterval
    period: int
    start_date: datetime
    end_date: datetime

    def __init__(self, info: SecurityInfo, candl_interval: CandleInterval, token, period: int, end_date: datetime = datetime.datetime.today()):
        super().__init__()
        self.info = info
        self.candle_interval = candl_interval
        self.__token = token
        self.period = period
        self.end_date = end_date
        if candl_interval == CandleInterval.CANDLE_INTERVAL_1_MIN:
            self.start_date = end_date - datetime.timedelta(minutes=period)
        else:
            if candl_interval == CandleInterval.CANDLE_INTERVAL_2_MIN:
                self.start_date = end_date - datetime.timedelta(minutes=period*2)
            else:
                if candl_interval == CandleInterval.CANDLE_INTERVAL_3_MIN:
                    self.start_date = end_date - datetime.timedelta(minutes=period*3)
                else:
                    if candl_interval == CandleInterval.CANDLE_INTERVAL_5_MIN:
                        self.start_date = end_date - datetime.timedelta(minutes=period*5)
                    else:
                        if candl_interval == CandleInterval.CANDLE_INTERVAL_10_MIN:
                            self.start_date = end_date - datetime.timedelta(minutes=period*10)
                        else:
                            if candl_interval == CandleInterval.CANDLE_INTERVAL_15_MIN:
                                self.start_date = end_date - datetime.timedelta(minutes=period*15)
                            else:
                                if candl_interval == CandleInterval.CANDLE_INTERVAL_30_MIN:
                                    self.start_date = end_date - datetime.timedelta(minutes=period*30)
                                else:
                                    if candl_interval == CandleInterval.CANDLE_INTERVAL_HOUR:
                                        self.start_date = end_date - datetime.timedelta(hours=period)
                                    else:
                                        if candl_interval == CandleInterval.CANDLE_INTERVAL_2_HOUR:
                                            self.start_date = end_date - datetime.timedelta(hours=period*2)
                                        else:
                                            if candl_interval == CandleInterval.CANDLE_INTERVAL_4_HOUR:
                                                self.start_date = end_date - datetime.timedelta(hours=period*4)
                                            else:
                                                if candl_interval == CandleInterval.CANDLE_INTERVAL_DAY:
                                                    self.start_date = end_date - datetime.timedelta(days=period)
                                                else:
                                                    if candl_interval == CandleInterval.CANDLE_INTERVAL_WEEK:
                                                        self.start_date = end_date - datetime.timedelta(weeks=period)
                                                    else:
                                                        if candl_interval == CandleInterval.CANDLE_INTERVAL_MONTH:
                                                            self.start_date = end_date - datetime.timedelta(
                                                                days=30*period)
