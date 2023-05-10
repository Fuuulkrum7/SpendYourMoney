from time import time

import function
import sqlalchemy
from PyQt5.QtCore import pyqtSignal
from tinkoff.invest import Client, RequestError, Share as tinkoffShare, \
    Bond as tinkoffBond, InstrumentIdType

from api_requests.securities_api import GetDividends, GetCoupons
from api_requests.security_getter import SecurityGetter, StandardQuery
from database.database_info import SecuritiesInfoTable, BondsInfoTable, \
    StocksInfoTable, SecuritiesInfo, StocksInfo, BondsInfo, DividendInfoTable,\
    DividendInfo, CouponInfoTable, CouponInfo
from database.database_interface import DatabaseInterface
from securities.securiries_types import SecurityType, StockType
from securities.securities import Security, Bond, Stock, SecurityInfo, \
    Dividend, Coupon


class GetSecurity(SecurityGetter):
    """
    Класс, отвечающий за загрузку данных по ЦБ.
    Использовать только в случае, если сформирован конкретный запрос
    Если надо все подряд, лучше будет использовать класс,
    который получает сразу все цб
    и загружает их в базу данных. Для загрузки цб для поисковика рекомендуется
    использовать следующие значения флагов:
    load_full_info = False, load_dividends = False, load_coupons = False
    """
    # Список цб
    securities: list[Security or Bond or Stock] = []
    # Список цб, которые требуется добавить в бд
    for_insert: list[Bond or Stock] = []
    # Загружать ли полную инфу о цб
    load_full_info: bool
    # Интересно, что же это такое... Даже не знаю
    status_code: int = 200
    # Список потоков для получения дивов/купонов.
    # Почему потоки. Это позволяет добавлять данные в бд корректно
    # Так как в момент загрузки купонов или
    # дивов мы ещё не знаем, какие будут id у цб
    # Которые мы только что скачали в базе данных
    sub_data: list[GetDividends or GetCoupons] = []
    data_downloaded = pyqtSignal(object)

    # Инициализация, всё банально
    def __init__(self, query: StandardQuery, on_finish: function, token: str,
                 insert_to_db=True, load_full_info=True, check_locally=True,
                 load_dividends: bool = True, load_coupons: bool = True,
                 check_only_locally: bool = False):
        super().__init__()
        self.query = query
        self.load_full_info = load_full_info
        self.data_downloaded.connect(on_finish)
        self.__token = token
        self.check_locally = check_locally
        self.check_only_locally = check_only_locally \
            if not check_only_locally or check_locally else check_locally
        self.insert_to_db = insert_to_db
        self.load_dividends = load_dividends
        self.load_coupons = load_coupons

    # Тут все банально
    def run(self) -> None:
        self.securities = []
        self.load_data()

        if self.for_insert and self.insert_to_db:
            try:
                self.insert_to_database()
            except Exception as e:
                print(e)
                self.status_code = 301

        self.data_downloaded.emit((self.status_code, self.securities))

    # Тоже банально
    def load_data(self):
        t = time()
        try:
            if self.check_locally:
                self.get_from_bd()
        except Exception as e:
            print(e)
            self.status_code = 300

        if not self.securities and not self.check_only_locally:
            self.get_from_api()

        # print(time() - t)

    def insert_to_database(self):
        # Подключаемся к базе данных
        db = DatabaseInterface()
        db.connect_to_db()

        i = 0
        # Перебираем массив ценных бумаг для получения данных
        print("at insert")

        for security in self.securities:
            # Защита от вылезания за границы
            if i < len(self.sub_data):
                sub_data = self.sub_data[i]
                i += 1

            # Имя таблицы, куда по умолчанию данные сохранятся
            table = SecuritiesInfoTable()

            # Если надо добавить данные в прочие таблицы
            if self.load_full_info:
                # Запускаем скрипт добавления данных в бд
                # Там передаем таблицу и данные, переведенные в словарь
                db.add_unique_data(
                    table.get_table(),
                    values=security.get_as_dict_security()
                )
                # Получаем курсор, из него мы
                # вытянем id только что добавленной цб
                cursor: sqlalchemy.engine.cursor = \
                    db.execute_sql("SELECT MAX(ID) FROM " + table.get_name())

                # Собственно, тут мы их и получаем.
                # И обновляем индекс security_id
                # Чтобы потом можно было найти цб в таблице
                for val in cursor:
                    security.set_security_id(val[0])
                    break

            # Если надо добавить облигации или акции, меняем таблицу на нужную
            if self.load_full_info and \
                    security.SECURITY_TYPE == SecurityType.BOND:
                table = BondsInfoTable()
            elif self.load_full_info and \
                    security.SECURITY_TYPE == SecurityType.STOCK:
                table = StocksInfoTable()

            # Добавление данных в нужную таблицу
            db.add_unique_data(
                table.get_table(),
                values=security.get_as_dict()
            )

            # Аналогично с получением индекса.
            # На этот раз будет использоваться собственный индекс
            cursor: sqlalchemy.engine.cursor = \
                db.execute_sql("SELECT MAX(ID) FROM " + table.get_name())
            for val in cursor:
                security.set_id(val[0])
                break

        for sub_data in self.sub_data:
            # Добавляем данные
            sub_data.insert_to_database()

        db.close_engine()

    def get_from_bd(self):
        # Подключаемся к бд
        db = DatabaseInterface()
        db.connect_to_db()

        # Формируем строку WHERE. Ищем по полям фиги, тикер, класс-код
        # И потом будет ещё поиск по имени, но там надо использовать
        # LIKE %query_text%, а питон ругается на наличие процентов в строке
        query = "WHERE "
        query += f"{SecuritiesInfo.FIGI.value} = '{self.query.get_figi()}' OR "
        query += f"{SecuritiesInfo.TICKER.value} = " \
                 f"'{self.query.get_ticker()}'"\
                 f" OR {SecuritiesInfo.CLASS_CODE.value} = " \
                 f"'{self.query.get_class_code()}'"
        query += f" OR {SecuritiesInfo.SECURITY_NAME.value} LIKE :par"

        # Получаем имя таблицы
        table = SecuritiesInfoTable().get_name()

        # Если не надо добавлять данные в прочие таблицы
        # (или же, что то же самое, получать прочие данные),
        # добавляем данные. Все в требуемом формате
        if not self.load_full_info:
            a = db.get_data_by_sql(
                {table: list(SecuritiesInfo)},
                table,
                where=query,
                params={"par": f"%{self.query.get_name()}%"}
            )

            # Перебираем массив полученных данных
            self.securities = [Security(**i) for i in a]
        # Если же надо проверять прочие таблицы
        else:
            # Тоже пишем WHERE, но, так как здесь используется JOIN,
            # то пишем через ON.
            # В остальном то же самое, разве что
            # добавляется проверка на совпадение
            # индекса таблицы всех цб и конкретной
            query = "ON "
            query += f"({table}.{SecuritiesInfo.FIGI.value}" \
                     f" = '{self.query.get_figi()}' OR "
            query += f"{table}.{SecuritiesInfo.SECURITY_NAME.value} " \
                     f"LIKE :par OR "
            query += f"{table}.{SecuritiesInfo.TICKER.value}" \
                     f" = '{self.query.get_ticker()}' OR "
            query += f"{table}.{SecuritiesInfo.CLASS_CODE.value}" \
                     f" = '{self.query.get_class_code()}') " \
                     f"AND {table}.{SecuritiesInfo.ID.value} = "

            # Получаем все из таблицы с акциями
            a = db.get_data_by_sql(
                {
                    table: list(SecuritiesInfo),
                    StocksInfoTable().get_name(): list(StocksInfo)
                },
                f"{table}",
                join=f"{StocksInfoTable().get_table()}",
                where=query + f"{StocksInfoTable().get_table()}."
                              f"{StocksInfo.security_id.value}"
                              f" AND {table}."
                              f"{SecuritiesInfo.SECURITY_TYPE.value} = 0",
                sort_query=[f"{StocksInfo.security_id.value} ASC"],
                params={"par": f"%{self.query.get_name()}%"}
            )
            # Получаем массив индексов цб
            indexes = [x["security_id"] for x in a]
            sub_data = []

            # Если цб есть
            if len(indexes):
                # Ищем по ним дивиденды в локальной базе данных
                sub_data = db.get_data_by_sql(
                    {DividendInfoTable().get_name(): list(DividendInfo)},
                    DividendInfoTable().get_name(),
                    where=f"WHERE {DividendInfo.security_id.value} "
                          f"IN ({', '.join(map(str, indexes))})",
                    sort_query=[f"{DividendInfo.security_id.value} ASC"]
                )

            # Здесь лежат дивиденды, распределенные по индексам
            # Так мы ускоряем их поиск при создании акций
            divs = {}

            if self.load_dividends:
                divs = {idx: [] for idx in indexes}

                # Распределяем их
                for value in sub_data:
                    div = Dividend(**value)
                    divs[div.security_id].append(div)
                sub_data.clear()

            # Перебираем полученные данные
            for value in a:
                # Создаем акцию
                stock = Stock(**value)

                # Если дивиденты по облигации в принципе есть
                if stock.div_yield_flag and self.load_dividends:
                    # Берем по индексу цб
                    div = divs[stock.info.id]

                    if not div:
                        # Если мы ее не нашли, проверяем, а вдруг мы ее просто
                        # забыли скачать
                        self.query.security_info.id = stock.info.id
                        self.query.security_info.figi = stock.info.figi

                        dividends = GetDividends(
                            self.query,
                            lambda x, y: x,
                            self.__token,
                            check_locally=False,
                            check_only_locally=self.check_only_locally
                        )
                        dividends.start()
                        dividends.wait()

                        # Обновляем значение
                        stock.dividend = dividends.dividend
                    else:
                        # Записываем данные по дивам
                        stock.dividend = div

                # Добавляем в массив
                self.securities.append(stock)

            # И облигации
            a = db.get_data_by_sql(
                    {
                        table: list(SecuritiesInfo),
                        BondsInfoTable().get_name(): list(BondsInfo)
                    },
                    f"{table}",
                    join=f"{BondsInfoTable().get_table()}",
                    where=query + f"{BondsInfoTable().get_table()}."
                                  f"{BondsInfo.security_id.value}"
                                  f" AND {table}."
                                  f"{SecuritiesInfo.SECURITY_TYPE.value} = 1",
                    params={"par": f"%{self.query.get_name()}%"}
                )
            # Получаем все индексы для купонов
            indexes = [x["security_id"] for x in a]

            if len(indexes):
                # Получаем купоны
                sub_data = db.get_data_by_sql(
                    {CouponInfoTable().get_name(): list(CouponInfo)},
                    CouponInfoTable().get_name(),
                    where=f"WHERE {CouponInfo.security_id.value} "
                          f"IN ({', '.join(map(str, indexes))})",
                    sort_query=[f"{CouponInfo.security_id.value} ASC"]
                )

            # Создаем из них словарь, чтобы по индексу цб получать сразу все
            coupons = {}

            if self.load_coupons:
                coupons = {idx: [] for idx in indexes}

                for value in sub_data:
                    coupon = Coupon(**value)
                    coupons[coupon.security_id].append(coupon)

            # Перебираем данные
            for value in a:
                # Из ключевых аргументов собираем облигацию
                bond = Bond(**value)

                if self.load_coupons:
                    coupon = coupons[bond.info.id]

                    # Если купонов в бд не было
                    if not coupon:
                        # Обновляем данные по id, чтобы запрос был короче
                        self.query.security_info.id = bond.info.id
                        self.query.security_info.figi = bond.info.figi

                        # Загружаем купоны
                        coup = GetCoupons(
                            self.query,
                            lambda x, y: x,
                            self.__token,
                            check_locally=False,
                            check_only_locally=self.check_only_locally
                        )
                        coup.start()
                        # Ждем, пока поток закончит работу
                        coup.wait()

                        # Обновляем данные по купонам
                        bond.coupon = coup.coupon
                    else:
                        # А если были, то сохраняем
                        bond.coupon = coupon

                # И добавляем облигацию в список существующих
                self.securities.append(bond)

        db.close_engine()
        # Чтобы не лезть в апи, если все хорошо и данные найдены
        self.insert_to_db = not len(self.securities)
        # Вывод количества найденных данных
        print("at get from db")
        print(len(self.securities))

    def get_from_api(self):
        # Получаем данные для запроса
        data = self.query.get_query()

        # Создаем подключение
        with Client(self.__token) as client:
            # Ищем данные
            try:
                r = client.instruments.find_instrument(query=data)
                results = r.instruments
            except RequestError as e:
                print(e)
                self.status_code = 401
                return

            # Фильтруем данные, чтобы были только акции и облигации
            results = list(filter(
                lambda x: x.instrument_type in ["share", "bond"], results
            ))

            # Защита от пустого запроса
            if len(results) == 0:
                self.status_code = 100
                return

            # Перебираем все полученные данные
            for result in results:
                # Обновляем данные, чтобы потом
                # было проще потом делать запрос
                self.query.security_info = SecurityInfo(
                    id=-2,
                    figi=result.figi,
                    ticker=result.ticker,
                    security_name=result.name,
                    class_code=result.class_code
                )

                # Создаем заранее переменную
                loaded_instrument: tinkoffBond or tinkoffShare

                # В зависимости от типа данных,
                # делаем запрос определенного типа
                if result.instrument_type == "bond":
                    try:
                        loaded_instrument = client.instruments.bond_by(
                            id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                            id=result.figi
                        ).instrument
                    except RequestError as e:
                        print(e)
                        self.status_code = 400
                        break

                elif result.instrument_type == "share":
                    try:
                        loaded_instrument: tinkoffShare = \
                             client.instruments.share_by(
                                id_type=InstrumentIdType.
                                INSTRUMENT_ID_TYPE_FIGI,
                                id=result.figi).instrument
                    # Защита от ошибок при запросе в интернет
                    except RequestError as e:
                        print(e)
                        self.status_code = 400
                        break

                # Определяем тип данных числом
                c = 0
                if result.instrument_type == "bond":
                    c = 1

                # Создаем цб
                security = Security(
                    class_code=loaded_instrument.class_code,
                    lot=loaded_instrument.lot,
                    currency=loaded_instrument.currency,
                    country=loaded_instrument.country_of_risk_name,
                    country_code=loaded_instrument.country_of_risk,
                    sector=loaded_instrument.sector,
                    security_type=SecurityType(c),
                    id=0,
                    figi=loaded_instrument.figi,
                    ticker=loaded_instrument.ticker,
                    security_name=loaded_instrument.name
                )

                if not self.load_full_info:
                    self.securities.append(security)

                # Загружаем акции и облигации
                sub = None
                # Если это облигация
                if security.security_type == SecurityType.BOND:
                    coupon = []
                    if self.load_coupons:
                        # Создаем поток для получения данных по купонам
                        sub = GetCoupons(
                            StandardQuery(self.query.security_info,
                                          self.query.query_text),
                            lambda x, y: x,
                            self.__token,
                            insert_to_db=False,
                            check_only_locally=self.check_only_locally
                        )

                        sub.start()
                        sub.wait()

                        # Обновляем статус-код
                        self.status_code = sub.status_code

                        coupon = sub.coupon

                    # Создаем облигацию
                    security = Bond(
                        security=security,
                        coupon_quantity_per_year=loaded_instrument.
                        coupon_quantity_per_year,
                        nominal=loaded_instrument.nominal,
                        amortization_flag=loaded_instrument.
                        amortization_flag,
                        maturity_date=loaded_instrument.maturity_date.
                        date(),
                        bond_id=-2,
                        aci_value=loaded_instrument.aci_value,
                        issue_size=loaded_instrument.issue_size,
                        issue_size_plan=loaded_instrument.issue_size_plan,
                        floating_coupon_flag=loaded_instrument.
                        floating_coupon_flag,
                        perpetual_flag=loaded_instrument.perpetual_flag,
                        coupon=coupon
                    )
                elif security.security_type == SecurityType.STOCK:
                    divs = []

                    if self.load_dividends and \
                            loaded_instrument.div_yield_flag:
                        # То же, но с дивидендами
                        sub = GetDividends(
                            StandardQuery(self.query.security_info,
                                          self.query.query_text),
                            lambda x, y: x,
                            self.__token,
                            insert_to_db=False,
                            check_only_locally=self.check_only_locally
                        )
                        sub.start()
                        sub.wait()

                        # И статус-код тоже обновляем
                        self.status_code = sub.status_code

                        divs = sub.dividend

                    # Создаем акцию
                    security = Stock(
                        security=security,
                        stock_id=-2,
                        ipo_date=loaded_instrument.ipo_date.date(),
                        issue_size=loaded_instrument.issue_size,
                        stock_type=StockType(loaded_instrument.share_type),
                        otc_flag=loaded_instrument.otc_flag,
                        div_yield_flag=loaded_instrument.div_yield_flag,
                        dividend=divs
                    )

                    # И если данные были реально получены
                    if security.info.id != -1:
                        if sub is not None:
                            # Добавляем поток и цб
                            self.sub_data.append(sub)
                        if self.load_full_info:
                            self.securities.append(security)

                        self.for_insert.append(security)

            # Пишем то, сколько инструментов мы нашли
            print(len(self.securities))

    def get_data(self) -> list[Security] or None:
        return self.securities
