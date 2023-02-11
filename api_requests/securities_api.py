from abc import ABC
from datetime import datetime
from time import time

import function
import sqlalchemy

from database.database_info import SecuritiesInfoTable, BondsInfoTable, \
    StocksInfoTable, CouponInfoTable, DividendInfoTable, SecuritiesInfo, StocksInfo, BondsInfo, CouponInfo, DividendInfo
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
            sub = dict(filter(lambda x: not (x[0] in "UID"), values.get_as_dict().items()))

            # Добавляем данные по купону
            query.append(sub)

        # Добавляем данные в бд
        db.add_data(
            table,
            query=query
        )

    # Поиск данных в бд
    def get_from_bd(self):
        # Создаем подключение
        db = DatabaseInterface()
        db.connect_to_db()

        # получаем id
        security_id = self.query.security_info.id
        # Если оно меньше 1, то даже не ищем, так как это означает,
        # что цб ещё ни разу не была загружена. Скорее всего
        if security_id <= 0:
            return
        # Получаем имя таблицы
        table = CouponInfoTable().get_table()

        # делаем простейший запрос
        a = db.get_data_by_sql(
            {table: list(CouponInfo)},
            table,
            where=f"WHERE {CouponInfo.security_id.name} = {security_id}"
        )

        # парсим данные в купоны
        self.coupon = [Coupon(**i) for i in a]
        # обновляем, надо ли нам добавлять данные в бд
        self.insert_to_db = not len(self.coupon)

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

                    # Если запрос был кривой и ничего не вернул, ругаемся
                    if not len(result) or self.query.security_info.id <= 0 and self.insert_to_db:
                        self.status_code = 510
                        return

                    # Иначе берем первую попавшуюся цб (смысла брать все нет,
                    # так как запрос должен подразумевать точечную загрузку по одной цб
                    figi = result[0].figi

                # и получаем данные по ней из апи
                sub_data = client.instruments.get_bond_coupons(
                    figi=figi,
                    from_=datetime(year=1971, month=1, day=1),
                    to=datetime(year=2100, month=1, day=1)
                ).events

            # парсим их в класс
            self.coupon = [
                Coupon(
                    coupon_id=-2,
                    security_id=self.query.security_info.id,
                    coupon_date=coupon.coupon_date,
                    fix_date=coupon.fix_date,
                    coupon_type=coupon.coupon_type,
                    pay_one_bond=coupon.pay_one_bond,
                    coupon_number=coupon.coupon_number
                ) for coupon in sub_data
            ]
        # Если что пошло не так, говорим об этом
        except Exception as e:
            print(e)
            self.status_code = 410


class GetDividends(SecurityGetter, ABC):
    """
    Класс, отвечающий за загрузку дивидендов по акциям.
    Является потоком, запуск различных действий только в виде потока,
    иначе тормозится основной, где работает интерфейс. Аналогичен полностью GetCoupons.
    В принципе можно было их объединить, но там в коде меняются переменные и строки,
    Так что придумывание родителя не то что бы имеет смысл, так как код это хоть и сократит,
    но при этом сильно усложнит структуру программы
    """
    dividend: list[Dividend] = None
    status_code: int = 200

    # Инициализация, все стандартно
    def __init__(self, query: StandardQuery, on_finish: function, token: str, check_locally=True, insert_to_db=True):
        super().__init__()
        self.query = query
        self.on_finish = on_finish
        self.__token = token
        self.check_locally = check_locally
        self.insert_to_db = insert_to_db

    # и тут тоже все так же, как в предыдущем классе
    def run(self) -> None:
        self.load_data()

        if self.dividend is not None and self.insert_to_db:
            try:
                self.insert_to_database()
            except Exception as e:
                print(e)
                self.status_code = 311

        self.on_finish(self.status_code)

    # И тут тоже, только имя переменной сменилось
    def load_data(self):
        try:
            if self.check_locally:
                self.get_from_bd()
        except Exception as e:
            print(e)
            self.status_code = 310

        if self.dividend is None:
            self.get_from_api()

    # И даже тут!
    def insert_to_database(self):
        if not len(self.dividend):
            self.status_code = 201
            return

        table = DividendInfoTable().get_table()
        db = DatabaseInterface()
        db.connect_to_db()

        query = []

        for values in self.dividend:
            sub = dict(filter(lambda x: not (x[0] in "UID"), values.get_as_dict().items()))

            query.append(sub)

        db.add_data(
            table,
            query=query
        )

    # и тут, ну, почти
    def get_from_bd(self):
        db = DatabaseInterface()
        db.connect_to_db()

        security_id = self.query.security_info.id
        if security_id <= 0:
            return
        table = DividendInfoTable().get_table()

        a = db.get_data_by_sql(
            {table: list(DividendInfo)},
            table,
            where=f"WHERE {DividendInfo.security_id.name} = {security_id}"
        )

        # Разве что тут мы вместо купонов создаем дивиденты, но как бы и так это понятно
        self.dividend = [Dividend(**i) for i in a]
        self.insert_to_db = not len(self.dividend)

    # А тут просто отличается класс, который мы создаем
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

            self.dividend = [
                Dividend(
                    div_value=div.dividend_net,
                    payment_date=div.payment_date,
                    declared_date=div.declared_date,
                    record_date=div.record_date,
                    last_buy_date=div.last_buy_date,
                    yield_value=div.yield_value,
                    div_id=-2,
                    security_id=self.query.security_info.id) for div in sub_data
            ]

        except Exception as e:
            print(e)
            self.status_code = 410


class GetSecurity(SecurityGetter, ABC):
    """
    Класс, отвечающий за загрузку данных по ЦБ.
    Использовать только в случае, если сформирован конкретный запрос
    Если надо все подряд, лучше будет использовать класс, который получает сразу все цб
    и загружает их в базу данных. В текущий момент (февраль 2023) он ещё не готов,
    но находится в планах
    """
    # Список цб
    securities: list[Security | Bond | Stock] = []
    # Добавлять ли цб
    add_to_other: bool
    # Интересно, что же это такое... Даже не знаю
    status_code: int = 200
    # Список потоков для получения дивов/купонов.
    # Почему потоки. Это позволяет добавлять данные в бд корректно
    # Так как в момент загрузки купонов/дивов мы ещё не знаем, какие будут id у цб
    # Которые мы только что скачали в базе данных
    sub_data: list[GetDividends | GetCoupons] = []

    # Инициализация, всё банально
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
        t = time()
        try:
            if self.check_locally:
                self.get_from_bd()
        except Exception as e:
            print(e)
            self.status_code = 300
            raise e

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
                    values=security.get_as_dict_security()
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
                values=security.get_as_dict()
            )

            cursor: sqlalchemy.engine.cursor = db.execute_sql("SELECT MAX(ID) FROM " + table.get_name())
            for i in cursor:
                security.set_id(i[0])
                break

    def get_from_bd(self):
        db = DatabaseInterface()
        db.connect_to_db()

        query_text = self.query.get_query()

        query = "WHERE "
        query += f"`{SecuritiesInfo.figi.name}` = '{query_text}' OR "
        query += f"`{SecuritiesInfo.ticker.name}` = '{query_text}' OR "
        query += f"`{SecuritiesInfo.class_code.name}` = '{query_text}'"
        table = SecuritiesInfoTable().get_name()

        if not self.add_to_other:
            a = db.get_data_by_sql(
                {table: list(SecuritiesInfo)},
                table,
                where=query
            )

            self.securities = [Security(**i) for i in a]

        else:
            query = "ON "
            query += f"({table}.{SecuritiesInfo.figi.name} = '{query_text}' OR "
            query += f"{table}.{SecuritiesInfo.ticker.name} = '{query_text}' OR "
            query += f"{table}.{SecuritiesInfo.class_code.name} = '{query_text}') " \
                     f"AND {table}.{SecuritiesInfo.ID.name} = "

            a = db.get_data_by_sql(
                {
                    table: list(SecuritiesInfo),
                    StocksInfoTable().get_name(): list(StocksInfo)
                },
                f"{table}",
                join=f"{StocksInfoTable().get_table()}",
                where=query + f"{StocksInfoTable().get_table()}.{StocksInfo.security_id.name}"
            )
            a.extend(
                db.get_data_by_sql(
                    {
                        table: list(SecuritiesInfo),
                        BondsInfoTable().get_name(): list(BondsInfo)
                    },
                    f"{table}",
                    join=f"{BondsInfoTable().get_table()}",
                    where=query + f"{BondsInfoTable().get_table()}.{BondsInfo.security_id.name}"
                )
            )

            for value in a:
                print(value)
                if value["security_type"] == SecurityType.BOND.value:
                    bond = Bond(**value)

                    self.query.security_info.id = bond.info.id
                    coupons = GetCoupons(
                        self.query,
                        lambda x: x,
                        self.__token
                    )
                    coupons.start()
                    coupons.join()

                    bond.coupon = coupons.coupon

                    self.securities.append(bond)
                else:
                    stock = Stock(**value)

                    self.query.security_info.id = stock.info.id
                    dividends = GetDividends(
                        self.query,
                        lambda x: x,
                        self.__token
                    )
                    dividends.start()
                    dividends.join()

                    stock.dividend = dividends.dividend

                    self.securities.append(stock)

        self.insert_to_db = not len(self.securities)
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
                    self.query.security_info = SecurityInfo(
                        id=-2,
                        figi=result.figi,
                        ticker=result.ticker,
                        security_name=result.name,
                        class_code=result.class_code
                    )

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
                        class_code=loaded_instrument.class_code,
                        lot=loaded_instrument.lot,
                        currency=loaded_instrument.currency,
                        country=loaded_instrument.country_of_risk_name,
                        sector=loaded_instrument.sector,
                        security_type=SecurityType(c),
                        id=0,
                        ID=0,
                        figi=loaded_instrument.figi,
                        ticker=loaded_instrument.ticker,
                        security_name=loaded_instrument.name
                    )

                    if self.add_to_other:
                        if security.security_type == SecurityType.BOND:
                            sub = GetCoupons(
                                StandardQuery(self.query.security_info, self.query.query_text),
                                lambda x: x,
                                self.__token,
                                insert_to_db=False
                            )

                            sub.start()
                            sub.join()

                            self.status_code = sub.status_code

                            t = time()
                            security = Bond(
                                security=security,
                                coupon_quantity_per_year=loaded_instrument.coupon_quantity_per_year,
                                nominal=loaded_instrument.nominal,
                                amortization_flag=loaded_instrument.amortization_flag,
                                maturity_date=loaded_instrument.maturity_date.date(),
                                bond_id=-2,
                                aci_value=loaded_instrument.aci_value,
                                issue_size=loaded_instrument.issue_size,
                                issue_size_plan=loaded_instrument.issue_size_plan,
                                floating_coupon_flag=loaded_instrument.floating_coupon_flag,
                                perpetual_flag=loaded_instrument.perpetual_flag,
                                coupon=sub.coupon
                            )
                            print(time() - t)

                            self.sub_data.append(sub)
                        elif security.security_type == SecurityType.STOCK:
                            sub = GetDividends(
                                StandardQuery(self.query.security_info, self.query.query_text),
                                lambda x: x,
                                self.__token,
                                insert_to_db=False
                            )
                            sub.start()
                            sub.join()

                            self.status_code = sub.status_code

                            t = time()
                            security = Stock(
                                security=security,
                                stock_id=-2,
                                ipo_date=loaded_instrument.ipo_date.date(),
                                issue_size=loaded_instrument.issue_size,
                                stock_type=StockType(loaded_instrument.share_type),
                                otc_flag=loaded_instrument.otc_flag,
                                div_yield_flag=loaded_instrument.div_yield_flag,
                                dividend=sub.dividend
                            )
                            print(time() - t)

                            self.sub_data.append(sub)
                        if security.info.id != -1:
                            self.securities.append(security)

            except RequestError as e:
                print(e)
                self.status_code = 400

            print(loaded_instrument)
            print(len(self.securities))
