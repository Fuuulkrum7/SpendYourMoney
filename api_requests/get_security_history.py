from datetime import datetime, timezone
from math import log10, ceil
from threading import Thread
from time import time

from PyQt5.QtCore import pyqtSignal
from tinkoff.invest import CandleInterval, Client, RequestError, \
    HistoricCandle, MoneyValue, Quotation

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
    """
    This class helps us to load info about securities price during period.
    If you download securities for long period, remember protect program from
    closing before data saving will be finished.
    """
    # history from db
    history: list[SecurityHistory] = []
    # history from server
    insert_data: list[SecurityHistory] = []
    __token: str
    # Временной период от и до
    _from: datetime
    to: datetime
    # Интервал временной (тип)
    interval: CandleInterval
    # Информация о цб
    info: SecurityInfo
    # Статус-код
    status_code: int = 200
    data_downloaded = pyqtSignal(object)

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
        self.data_downloaded.connect(on_finish)

    def run(self) -> None:
        t = time()

        # Ищем и удаленно, и в бд
        self.get_from_bd()
        print(time() - t)
        self.get_from_api()

        print(time() - t)

        # Создаем поток для функции и отправляем курс

        self.data_downloaded.emit((self.status_code, self.history))

        # Попутно запускаем сохранение в бд
        if self.insert_data:
            self.insert_to_database()

    def insert_to_database(self):
        # Подключаемся к бд
        db = DatabaseInterface()
        db.connect_to_db()

        # Таблица, куда добавляем данные
        table = SecuritiesHistoryTable().get_table()

        # Массив данных для добавления
        query = [val.get_as_dict_candle(self.interval)
                 for val in self.insert_data]

        # Добавляем (уникальные) данные
        db.add_unique_data(
            table,
            query=query
        )

        # Закрываем подключение
        db.close_engine()

    # Здесь мы ищем данные локально (по курсу цб)
    def get_from_bd(self):
        # Создаем подключение к бд
        db = DatabaseInterface()
        db.connect_to_db()

        # Переводим время в нужный часовой пояс
        self._from = self._from.replace(tzinfo=timezone.utc)
        self.to = self.to.replace(tzinfo=timezone.utc)

        # Таблица, откуда берем данные
        table = SecuritiesHistoryTable()
        # Ищем данные с таким id ценной бумаги и в нужном временном промежутке
        where = f"WHERE {SecuritiesHistory.security_id.value}={self.info.id}" \
                f" AND {SecuritiesHistory.info_time.value} " \
                f" BETWEEN '{self._from.strftime('%y-%m-%d %H:%M:%S')}'" \
                f" AND '{self.to.strftime('%y-%m-%d %H:%M:%S')}' "

        # И тип временной свечи тот, который был запрошен
        where += f" AND {SecuritiesHistory.CANDLE_INTERVAL.value} = " \
                 f"{self.interval.value}"

        # Получаем историю курса в порядке возрастания времени
        histories = db.get_data_by_sql(
            {table.get_name(): [SecuritiesHistory.security_id,
                                SecuritiesHistory.info_time,
                                SecuritiesHistory.volume,
                                SecuritiesHistory.price]},
            table.get_name(),
            where=where,
            sort_query=[f"{SecuritiesHistory.info_time.value} ASC"]
        )

        # Парсим данные
        self.history = [SecurityHistory(**history) for history in histories]

        db.close_engine()

    # Здесь обращаемся к серверу
    def get_from_api(self):
        result = ()
        # Создаем подключение
        with Client(self.__token) as client:
            # Грузим все данные
            try:
                result = tuple(client.get_all_candles(
                    figi=self.info.figi,
                    from_=self._from,
                    to=self.to,
                    interval=self.interval,
                ))

            except RequestError as e:
                print(e)
                self.status_code = 400

            print("data loaded")
            # Парсим данные в классы
            result = list(map(self.get_from_candle, result))
            print("data parsed")

            # Оставляем для добавления только те свечи, которые вы ещё не
            # добавили в бд
            self.insert_data = list(
                set(result) - set(self.history)
            )

            # Если какие-либо данные были получены, то ставим их, так как
            # в таком случае у нас тут данные будут более полными, нежели
            # данные из бд
            if result:
                self.history = result
            self.insert_data.sort(key=lambda x: x.info_time)

    # Парсим данные в класс
    def get_from_candle(self, candle: HistoricCandle) -> SecurityHistory:
        return SecurityHistory(
            price=convert_money_value(candle.close),
            security_id=self.info.id,
            volume=candle.volume,
            info_time=candle.time
        )

    def get_data(self):
        return self.history
