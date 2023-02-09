from abc import ABC
from datetime import datetime

import function
import sqlalchemy

from database.database_info import SecuritiesInfoTable, BondsInfoTable, \
    StocksInfoTable, CouponInfoTable, DividendInfoTable, SecuritiesInfo
from api_requests.security_getter import StandardQuery, SecurityGetter
from securities.securiries_types import SecurityType, StockType
from securities.securities import Security, Stock, Bond, SecurityInfo, Coupon, Dividend
from database.database_interface import DatabaseInterface


from tinkoff.invest import InstrumentIdType, Share as tinkoffShare, Bond as tinkoffBond
from tinkoff.invest import Client
from tinkoff.invest.exceptions import RequestError


"""
Информация о статус-кодах

100 - данных нет

2** - все успешно загружено
200 все операции прошли успешно
201 - при добавлении доп. данных

3** - что-то пошло не так с бд
300 - ошибка в получении данных из бд, конкретно тут -
не критичная.
301 - критическая ошибка при добавлении в бд
310 и 311 аналогично, но для доп. данных,
то есть для купонов и дивидендов

4** - ошибка при загрузке данных из интернета. Критические все
400 - ошибка при загрузке данных основных
410 - дополнительных
"""


class GetCoupons(SecurityGetter, ABC):
    """
    Класс, отвечающий за загрузку купонов по облигациям.
    Является потоком, запуск различных действий только в виде потока,
    иначе тормозится основной, где работает интерфейс
    """
    # Заготовка под купоны
    coupon: list[Coupon] = None
    # Статус-код, все банально
    status_code: int = 200

    def __init__(self, query: StandardQuery, on_finish: function, token: str, check_locally=True, insert_to_db=True):
        # Просто сохраняем данные по переменным
        super().__init__()
        self.query = query
        self.on_finish = on_finish
        self.__token = token
        self.check_locally = check_locally
        self.insert_to_db = insert_to_db

    def run(self) -> None:
        # запускаем загрузку данных
        self.load_data()

        # Если они загружены и их надо добавить
        if self.coupon is not None and self.insert_to_db:
            # Пробуем их добавить
            try:
                self.insert_to_database()
            except Exception as e:
                print(e)
                # В случае ошибки добавления, обозначаем
                self.status_code = 311

        # Вызов функции
        self.on_finish(self.status_code)

    def load_data(self):
        # Если надо проверять локально, делам это
        try:
            if self.check_locally:
                self.get_from_bd()
        except Exception as e:
            print(e)
            self.status_code = 310

        # Если мы данные все ещё не загрузили,
        # лезем в апи
        if self.coupon is None:
            self.get_from_api()

    def insert_to_database(self):
        # Защита от вызова из вне. Так-то ранее уже проверка есть
        # Ну и от пустого добавления данных тоже есть.
        if self.coupon is None or not len(self.coupon):
            self.status_code = 201
            return

        # Таблица, куда добавляем
        table = CouponInfoTable().get_table()
        # Создаем интерфейс для работы с бд
        # и подключаемся к ней
        db = DatabaseInterface()
        db.connect_to_db()

        # Массив данных под запрос
        query = []

        # Перебираем купоны
        for values in self.coupon:
            sub = {}
            # Перебираем каждое из полей купона
            n = values.get_as_database_value()
            for value in n:
                # Если поле не автоматически добавляемое
                if not (value.get_row_name() in ["ID", "UID"]):
                    # Ставим в соответствие имени столбца значение
                    sub[value.get_row_name()] = value.to_db_value()

            # Добавляем данные по акции
            query.append(sub)

        # Добавляем данные в бд
        db.add_data(
            table,
            query=query
        )

    # Поиск данных в бд
    def get_from_bd(self):
        pass

    def get_from_api(self):
        # Получаем фиги из запроса,
        # так как этот метод в апи работает только с фиги
        figi = self.query.security_info.figi

        try:
            # создаем соединение
            with Client(self.__token) as client:
                # Если фиги пуст
                if not len(figi):
                    # получаем данные для запроса
                    data = self.query.get_query()

                    # делаем запрос
                    r = client.instruments.find_instrument(query=data)
                    result = r.instruments

                    # оставляем только те данные, которые подходят по запросу
                    result = list(filter(lambda x: x.instrument_type == "bond", result))

                    if not len(result) or self.query.security_info.id <= 0 and self.insert_to_db:
                        self.status_code = 510
                        return

                    figi = result[0].figi

                sub_data = client.instruments.get_bond_coupons(
                    figi=figi,
                    from_=datetime(year=1971, month=1, day=1),
                    to=datetime(year=2100, month=1, day=1)
                ).events

            self.coupon = [Coupon(i, -2, self.query.security_info.id) for i in sub_data]
        except Exception as e:
            print(e)
            self.status_code = 410


class GetDividends(SecurityGetter, ABC):
    dividend: list[Dividend] = None
    status_code: int = 200

    def __init__(self, query: StandardQuery, on_finish: function, token: str, check_locally=True, insert_to_db=True):
        super().__init__()
        self.query = query
        self.on_finish = on_finish
        self.__token = token
        self.check_locally = check_locally
        self.insert_to_db = insert_to_db

    def run(self) -> None:
        self.load_data()

        if self.dividend is not None and self.insert_to_db:
            try:
                self.insert_to_database()
            except Exception as e:
                print(e)
                self.status_code = 311

        self.on_finish(self.status_code)

    def load_data(self):
        try:
            if self.check_locally:
                self.get_from_bd()
        except Exception as e:
            print(e)
            self.status_code = 310

        if self.dividend is None:
            self.get_from_api()

    def insert_to_database(self):
        if not len(self.dividend):
            self.status_code = 201
            return

        table = DividendInfoTable().get_table()
        db = DatabaseInterface()
        db.connect_to_db()

        query = []

        for values in self.dividend:
            sub = {}
            n = values.get_as_database_value()
            for value in n:
                if not (value.get_row_name() in ["ID", "UID"]):
                    sub[value.get_row_name()] = value.to_db_value()

            query.append(sub)

        db.add_data(
            table,
            query=query
        )

    def get_from_bd(self):
        pass

    def get_from_api(self):
        figi = self.query.security_info.figi

        try:
            with Client(self.__token) as client:
                if not len(figi):
                    data = self.query.get_query()

                    r = client.instruments.find_instrument(query=data)
                    result = r.instruments

                    result = list(filter(lambda x: x.instrument_type == "share", result))

                    if not len(result):
                        self.status_code = 510
                        return

                    figi = result[0].figi

                sub_data = client.instruments.get_dividends(
                    figi=figi,
                    from_=datetime(year=1990, month=1, day=1),
                    to=datetime(year=2100, month=1, day=1)
                ).dividends

            self.dividend = [Dividend(i, -2, -2) for i in sub_data]

        except Exception as e:
            print(e)
            self.status_code = 410


class GetSecurity(SecurityGetter, ABC):
    securities: list[Security | Bond | Stock] = []
    add_to_other: bool
    status_code: int = 200
    sub_data: list[GetDividends | GetCoupons] = []

    def __init__(self, query: StandardQuery, on_finish: function, token: str,
                 insert_to_db=True, add_to_other=True, check_locally=True):
        super().__init__()
        self.query = query
        self.add_to_other = add_to_other
        self.on_finish = on_finish
        self.__token = token
        self.check_locally = check_locally
        self.insert_to_db = insert_to_db

    def run(self) -> None:
        self.load_data()

        if self.securities and self.insert_to_db:
            try:
                self.insert_to_database()
            except Exception as e:
                print(e)
                self.status_code = 301

        self.on_finish(self.status_code)

    def load_data(self):
        from time import time
        t = time()
        try:
            if self.check_locally:
                self.get_from_bd()
        except Exception as e:
            print(e)
            self.status_code = 300

        if not self.securities:
            self.get_from_api()

        print(time() - t)

    def insert_to_database(self):
        db = DatabaseInterface()
        db.connect_to_db()

        for security, sub_data in zip(self.securities, self.sub_data):
            table = SecuritiesInfoTable()

            if self.add_to_other:
                db.add_data(
                    table.get_table(),
                    values=security.get_as_database_value_security()
                )
                cursor: sqlalchemy.engine.cursor = db.execute_sql("SELECT MAX(ID) FROM " + table.get_name())

                for i in cursor:
                    security.set_security_id(i[0])
                    break

                if security.security_type == SecurityType.BOND or security.div_yield_flag:
                    sub_data.insert_to_database()

            if security.security_type == SecurityType.BOND:
                table = BondsInfoTable()
            elif security.security_type == SecurityType.STOCK:
                table = StocksInfoTable()

            db.add_data(
                table.get_table(),
                values=security.get_as_database_value()
            )

            cursor: sqlalchemy.engine.cursor = db.execute_sql("SELECT MAX(ID) FROM " + table.get_name())
            for i in cursor:
                security.set_id(i[0])
                break

    def get_from_bd(self):
        db = DatabaseInterface()
        db.connect_to_db()

        query = "WHERE "
        query += f"{SecuritiesInfo.figi} = {self.query.get_query()} OR "
        query += f"{SecuritiesInfo.security_name} LIKE %{self.query.get_query()}% OR "
        query += f"{SecuritiesInfo.ticker} = {self.query.get_query()} OR "
        query += f"{SecuritiesInfo.class_code} = {self.query.get_query()}"

        a = db.get_data_by_sql(
            SecuritiesInfoTable().get_name(),
            [value for value in SecuritiesInfo],
            where=query
        )

        self.securities = [Security(i) for i in a]

        if self.add_to_other:
            for security in self.securities:
                query = f"WHERE security_id = {security.info.id}"
                a = db.get_data_by_sql(
                    f"{BondsInfoTable().get_name()} "
                    f"{StocksInfoTable().get_table()}",
                    [],
                    where=query
                )
        print(len(self.securities))

    def get_from_api(self):
        data = self.query.get_query()

        with Client(self.__token) as client:
            r = client.instruments.find_instrument(query=data)
            results = r.instruments

            results = list(filter(lambda x: x.instrument_type in ["share", "bond"], results))

            if len(results) == 0:
                self.status_code = 100
                return

            try:
                for result in results:
                    self.query.security_info = SecurityInfo(-2, result.figi, result.ticker, result.name)

                    loaded_instrument: tinkoffShare | tinkoffBond

                    if result.instrument_type == "bond":
                        loaded_instrument = client.instruments.bond_by(
                            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                            id=result.figi
                        ).instrument

                    elif result.instrument_type == "share":
                        loaded_instrument: tinkoffShare = client.instruments.share_by(
                            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                            id=result.figi
                        ).instrument

                    else:
                        return

                    c = 0
                    if result.instrument_type == "bond":
                        c = 1

                    security = Security(
                        loaded_instrument.class_code,
                        loaded_instrument.lot,
                        loaded_instrument.currency,
                        loaded_instrument.country_of_risk_name,
                        loaded_instrument.sector,
                        SecurityType(c),
                        -2,
                        loaded_instrument.figi,
                        loaded_instrument.ticker,
                        loaded_instrument.name
                    )

                    if self.add_to_other:
                        if security.security_type == SecurityType.BOND:
                            sub_data = GetCoupons(
                                StandardQuery(security.info, self.query.query_text),
                                lambda x: x,
                                self.__token,
                                insert_to_db=False
                            )
                            sub_data.start()
                            sub_data.join()

                            self.status_code = sub_data.status_code

                            security = Bond(
                                security,
                                [
                                    loaded_instrument.coupon_quantity_per_year,
                                    loaded_instrument.nominal,
                                    loaded_instrument.amortization_flag,
                                    loaded_instrument.maturity_date.date(),
                                    -2,
                                    loaded_instrument.aci_value,
                                    loaded_instrument.issue_size,
                                    loaded_instrument.issue_size_plan,
                                    loaded_instrument.floating_coupon_flag,
                                    loaded_instrument.perpetual_flag
                                ],
                                sub_data.coupon
                            )

                            self.sub_data.append(sub_data)
                        elif security.security_type == SecurityType.STOCK:
                            sub_data = GetDividends(
                                StandardQuery(security.info, self.query.query_text),
                                lambda x: x,
                                self.__token,
                                insert_to_db=False
                            )
                            sub_data.start()
                            sub_data.join()

                            self.status_code = sub_data.status_code

                            security = Stock(
                                security,
                                [
                                    -2,
                                    loaded_instrument.ipo_date.date(),
                                    loaded_instrument.issue_size,
                                    StockType(loaded_instrument.share_type),
                                    loaded_instrument.otc_flag,
                                    loaded_instrument.div_yield_flag
                                ],
                                sub_data.dividend
                            )
                            self.sub_data.append(sub_data)

                        if security.info.id != -1:
                            self.securities.append(security)

            except RequestError as e:
                print(e)
                self.status_code = 400

            print(loaded_instrument)
            print(len(self.securities))
