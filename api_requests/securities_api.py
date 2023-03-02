from datetime import datetime
from threading import Thread

import function

from database.database_info import CouponInfoTable, DividendInfoTable, \
    CouponInfo, DividendInfo
from api_requests.security_getter import StandardQuery, SecurityGetter
from securities.securities import Coupon, Dividend
from database.database_interface import DatabaseInterface

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


class GetCoupons(SecurityGetter):
    """
    Класс, отвечающий за загрузку купонов по облигациям.
    Является потоком, запуск различных действий только в виде потока,
    иначе тормозится основной, где работает интерфейс
    """
    # Заготовка под купоны
    coupon: list[Coupon] = []
    # Статус-код, все банально
    status_code: int = 200

    def __init__(self, query: StandardQuery, on_finish: function, token: str,
                 check_locally=True, insert_to_db=True,
                 check_only_locally=False):
        # Просто сохраняем данные по переменным
        super().__init__()
        self.query = query
        self.on_finish = on_finish
        self.__token = token
        self.check_locally = check_locally
        self.insert_to_db = insert_to_db
        self.check_only_locally = check_only_locally

    def run(self) -> None:
        # запускаем загрузку данных
        self.load_data()

        # Если они загружены и их надо добавить
        if self.coupon and self.insert_to_db:
            # Пробуем их добавить
            try:
                self.insert_to_database()
            except Exception as e:
                print(e)
                # В случае ошибки добавления, обозначаем
                self.status_code = 311

        # Вызов функции
        Thread(target=self.on_finish,
               args=(self.status_code, self.coupon)).start()

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
        if not self.coupon and not self.check_only_locally:
            self.get_from_api()

    def insert_to_database(self):
        # Защита от вызова из вне. Так-то ранее уже проверка есть
        # Ну и от пустого добавления данных тоже есть.
        if not self.coupon:
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
            # Добавляем данные по купону
            query.append(values.get_as_dict())

        # Добавляем данные в бд
        db.add_unique_data(
            table,
            query=query
        )

        db.close_engine()

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
            where=f"WHERE {CouponInfo.security_id.value} = {security_id}"
        )

        # парсим данные в купоны
        self.coupon = [Coupon(**i) for i in a]
        # обновляем, надо ли нам добавлять данные в бд
        self.insert_to_db = not len(self.coupon)

        db.close_engine()

    def get_from_api(self):
        # Получаем фиги из запроса,
        # так как этот метод в апи работает только с фиги
        figi = self.query.security_info.figi

        with Client(self.__token) as client:
            # Если фиги пуст
            if not len(figi):
                # получаем данные для запроса
                data = self.query.get_query()

                # делаем запрос
                try:
                    r = client.instruments.find_instrument(query=data)
                    result = r.instruments
                except RequestError as e:
                    print(e)
                    self.status_code = 410
                    return

                # оставляем только те данные, которые подходят по запросу
                result = list(filter(
                    lambda x: x.instrument_type == "bond", result
                ))

                # Если запрос был кривой и ничего не вернул, ругаемся
                if not len(result) or self.query.security_info.id <= 0\
                        and self.insert_to_db:
                    self.status_code = 510
                    return

                # Иначе берем первую попавшуюся цб (смысла брать все нет,
                # так как запрос должен подразумевать
                # точечную загрузку по одной цб
                figi = result[0].figi

            try:
                # и получаем данные по ней из апи
                sub_data = client.instruments.get_bond_coupons(
                    figi=figi,
                    from_=datetime(year=1971, month=1, day=1),
                    to=datetime(year=2100, month=1, day=1)
                ).events
            except RequestError as e:
                print(e)
                self.status_code = 410
                return

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

    def get_data(self):
        return self.coupon


class GetDividends(SecurityGetter):
    """
    Класс, отвечающий за загрузку дивидендов по акциям.
    Является потоком, запуск различных действий только в виде потока,
    иначе тормозится основной, где работает интерфейс.
    Аналогичен полностью GetCoupons.
    В принципе можно было их объединить, но
    там в коде меняются переменные и строки,
    Так что придумывание родителя не то что бы
     имеет смысл, так как код это хоть и сократит,
    но при этом сильно усложнит структуру программы
    """
    dividend: list[Dividend] = []
    status_code: int = 200

    # Инициализация, все стандартно
    def __init__(self, query: StandardQuery, on_finish: function,
                 token: str, check_locally=True, insert_to_db=True,
                 check_only_locally=False):
        super().__init__()
        self.query = query
        self.on_finish = on_finish
        self.__token = token
        self.check_locally = check_locally
        self.insert_to_db = insert_to_db
        self.check_only_locally = check_only_locally

    # и тут тоже все так же, как в предыдущем классе
    def run(self) -> None:
        self.load_data()

        if self.dividend and self.insert_to_db:
            try:
                self.insert_to_database()
            except Exception as e:
                print(e)
                self.status_code = 311

        Thread(target=self.on_finish,
               args=(self.status_code, self.dividend)).start()

    # И тут тоже, только имя переменной сменилось
    def load_data(self):
        try:
            if self.check_locally:
                self.get_from_bd()
        except Exception as e:
            print(e)
            self.status_code = 310

        if not self.dividend and not self.check_only_locally:
            self.get_from_api()

    # И даже тут!
    def insert_to_database(self):
        if not self.dividend:
            self.status_code = 201
            return

        table = DividendInfoTable().get_table()
        db = DatabaseInterface()
        db.connect_to_db()

        query = []

        for values in self.dividend:
            query.append(values.get_as_dict())

        db.add_unique_data(
            table,
            query=query
        )

        db.close_engine()

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
            where=f"WHERE {DividendInfo.security_id.value} = {security_id}"
        )

        # Разве что тут мы вместо купонов создаем
        # дивиденты, но как бы и так это понятно
        self.dividend = [Dividend(**i) for i in a]
        self.insert_to_db = not len(self.dividend)
        db.close_engine()

    # А тут просто отличается класс, который мы создаем
    def get_from_api(self):
        figi = self.query.security_info.figi

        with Client(self.__token) as client:
            if not len(figi):
                data = self.query.get_query()

                try:
                    r = client.instruments.find_instrument(query=data)
                    result = r.instruments
                except RequestError as e:
                    print(e)
                    self.status_code = 410
                    return

                result = list(filter(
                    lambda x: x.instrument_type == "share", result
                ))

                if not len(result):
                    self.status_code = 510
                    return

                figi = result[0].figi

            try:
                sub_data = client.instruments.get_dividends(
                    figi=figi,
                    from_=datetime(year=1990, month=1, day=1),
                    to=datetime(year=2100, month=1, day=1)
                ).dividends
            except RequestError as e:
                print(e)
                self.status_code = 410
                return

        self.dividend = [
            Dividend(
                div_value=div.dividend_net,
                payment_date=div.payment_date,
                declared_date=div.declared_date,
                record_date=div.record_date,
                last_buy_date=div.last_buy_date,
                yield_value=div.yield_value,
                div_id=-2,
                security_id=self.query.security_info.id)
            for div in sub_data
        ]

    def get_data(self):
        return self.dividend
