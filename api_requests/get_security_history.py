from datetime import datetime
from threading import Thread
from time import time

from tinkoff.invest import CandleInterval

from database.database_info import SecuritiesHistory, SecuritiesHistoryTable
from database.database_interface import DatabaseInterface
from securities.securities import SecurityInfo
from securities.securities_history import SecurityHistory


class GetSecurityHistory(Thread):
    history: list[SecurityHistory]
    __token: str
    _from: datetime
    to: datetime
    interval: CandleInterval
    insert: bool
    info: SecurityInfo

    def __init__(self, token: str, _from: datetime, to: datetime,
                 interval: CandleInterval, info: SecurityInfo):
        super().__init__()

        self._from = _from
        self.to = to
        self.__token = token
        self.interval = interval
        self.info = info

    def run(self) -> None:
        t = time()
        self.load_data()
        print(time() - t)

        if self.insert:
            self.insert_to_db()

    def load_data(self):
        db = DatabaseInterface()
        db.connect_to_db()

        if self.interval == CandleInterval.CANDLE_INTERVAL_1_MIN:
            dtime = datetime()
        elif self.interval == CandleInterval.CANDLE_INTERVAL_5_MIN:
            dtime = datetime()
        elif self.interval == CandleInterval.CANDLE_INTERVAL_15_MIN:
            dtime = datetime()
        elif self.interval == CandleInterval.CANDLE_INTERVAL_HOUR:
            dtime = datetime()
        else:
            dtime = datetime()


        table = SecuritiesHistoryTable()
        where = f"{SecuritiesHistory.security_id.value} = {self.info.id}"
        where += f"AND {SecuritiesHistory.info_time.value} " \
                 f"BETWEEN {self._from} AND {self.to}" \
                 f""

        db.get_data_by_sql(
            {table.get_name(): list(SecuritiesHistory)},
            table.get_name(),
            where=where,
            sort_query=[f"{SecuritiesHistory.info_time.value} ASC"]
        )

        db.close_engine()

        if self.interval == CandleInterval.CANDLE_INTERVAL_1_MIN:
            a = divmod((self.to - self._from).total_seconds(), 60)[0]
            self.insert = len(self.history) != a
        elif self.interval == CandleInterval.CANDLE_INTERVAL_5_MIN:
            a = divmod((self.to - self._from).total_seconds(), 60)[0] // 5
            self.insert = len(self.history) != a
        elif self.interval == CandleInterval.CANDLE_INTERVAL_15_MIN:
            a = divmod((self.to - self._from).total_seconds(), 60)[0] // 15
            self.insert = len(self.history) != a
        elif self.interval == CandleInterval.CANDLE_INTERVAL_HOUR:
            a = divmod((self.to - self._from).total_seconds(), 360)[0]
            self.insert = len(self.history) != a
        else:
            a = divmod((self.to - self._from).total_seconds(), 360)[0] // 24
            self.insert = len(self.history) != a

    def insert_to_db(self):
        pass
