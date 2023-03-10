from datetime import datetime, timezone
from math import log10, ceil
from threading import Thread
from time import time

from tinkoff.invest import CandleInterval, Client, RequestError, \
    HistoricCandle, MoneyValue, Quotation

from api_requests.security_getter import SecurityGetter
from database.database_info import SecuritiesHistory, SecuritiesHistoryTable
from database.database_interface import DatabaseInterface
from securities.securities import SecurityInfo
from securities.securities_history import SecurityHistory


def convert_money_value(data: MoneyValue or Quotation or float):
    if isinstance(data, float):
        return data
    return data.units + data.nano / 10 ** ceil(
        log10(data.nano if data.nano > 0 else 1)
    )


class GetSecurityHistory(Thread):
    history: list[SecurityHistory] = []
    insert_data: list[SecurityHistory] = []
    __token: str
    _from: datetime
    to: datetime
    interval: CandleInterval
    info: SecurityInfo
    status_code: int = 200

    def __init__(self, token: str = "", _from: datetime = None,
                 to: datetime = None,
                 interval: CandleInterval =
                 CandleInterval.CANDLE_INTERVAL_UNSPECIFIED,
                 info: SecurityInfo = None, on_finish=None):
        super().__init__()

        self._from = _from
        self.to = to
        self.__token = token
        self.interval = interval
        self.info = info
        self.on_finish = on_finish

    def run(self) -> None:
        t = time()

        self.get_from_bd()
        self.get_from_api()

        print(time() - t)

        if self.insert_data:
            self.insert_to_database()

        Thread(target=self.on_finish,
               args=(self.status_code, self.history)).start()

    def insert_to_database(self):
        db = DatabaseInterface()
        db.connect_to_db()

        table = SecuritiesHistoryTable().get_table()

        query = [val.get_as_dict() for val in self.insert_data]

        db.add_unique_data(
            table,
            query=query
        )

        db.close_engine()

    def get_from_bd(self):
        # TODO fix bug with local data load
        db = DatabaseInterface()
        db.connect_to_db()

        self._from = self._from.replace(tzinfo=timezone.utc)
        self.to = self.to.replace(tzinfo=timezone.utc)

        table = SecuritiesHistoryTable()
        where = f"WHERE {SecuritiesHistory.security_id.value}={self.info.id}" \
                f" AND {SecuritiesHistory.info_time.value} " \
                f" BETWEEN '{self._from.strftime('%y-%m-%d %H:%M:%S')}'" \
                f" AND '{self.to.strftime('%y-%m-%d %H:%M:%S')}' "

        millis_time = f"UNIX_TIMESTAMP({SecuritiesHistory.info_time.value})"
        if self.interval == CandleInterval.CANDLE_INTERVAL_5_MIN:
            where += f" AND {millis_time} % 300 = 0"
        elif self.interval == CandleInterval.CANDLE_INTERVAL_15_MIN:
            where += f" AND {millis_time} % 900 = 0"
        elif self.interval == CandleInterval.CANDLE_INTERVAL_HOUR:
            where += f" AND {millis_time} % 3600 = 0"
        elif self.interval == CandleInterval.CANDLE_INTERVAL_DAY:
            where += f" AND TIMEDIFF(info_time, CAST(CAST(info_time AS DATE)" \
                     f" AS DATETIME)) = CAST(\"07:00:00\" as TIME)"

        histories = db.get_data_by_sql(
            {table.get_name(): list(SecuritiesHistory)},
            table.get_name(),
            where=where,
            sort_query=[f"{SecuritiesHistory.info_time.value} ASC"]
        )

        for history in histories:
            self.history.append(
                SecurityHistory(
                    info_time=history[SecuritiesHistory.info_time.value],
                    security_id=self.info.id,
                    price=history[SecuritiesHistory.price.value],
                    volume=history[SecuritiesHistory.volume.value]
                )
            )

        db.close_engine()

    def get_from_api(self):
        with Client(self.__token) as client:
            try:
                result = client.get_all_candles(
                    figi=self.info.figi,
                    from_=self._from,
                    to=self.to,
                    interval=self.interval,
                )
            except RequestError as e:
                print(e)
                self.status_code = 400

            result = list(map(self.get_from_candle, result))

            result = list(filter(
                lambda x: not (x in self.history),
                result
            ))

            self.history.extend(result)
            self.insert_data = result

    def get_from_candle(self, candle: HistoricCandle) -> SecurityHistory:
        return SecurityHistory(
            price=convert_money_value(candle.close),
            security_id=self.info.id,
            volume=candle.volume,
            info_time=candle.time
        )

    def get_data(self):
        return self.history
