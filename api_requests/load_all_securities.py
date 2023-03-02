from time import time

import function
from threading import Thread
from tinkoff.invest import Client, RequestError, Share as tinkoffShare, \
    Bond as tinkoffBond, InstrumentStatus

from database.database_info import SecuritiesInfoTable, BondsInfoTable, \
    StocksInfoTable, SecuritiesInfo
from database.database_interface import DatabaseInterface
from securities.securiries_types import SecurityType, StockType
from securities.securities import Bond, Stock


class LoadAllSecurities(Thread):
    """
    Класс, отвечающий за загрузку всех цб без доп. информации
    """
    # Список цб
    securities: list[Bond or Stock] = []
    # Статус-код
    # 200 - успешно
    # 301 - ошибка при добавлении
    # 400 - ошибка при загрузке (любая)
    # 402 - при загрузке облигаций
    # 403 - при загрузке акций
    # 404 - первые две одновременно, данных нет
    # 405 - ошибка неизвестного типа, просто что-то пошло не так
    status_code: int = 200

    def __init__(self, on_finish: function, token: str):
        super().__init__()

        self.on_finish = on_finish
        self.__token = token

    # Тут все банально, запускаем все методы
    def run(self) -> None:
        # Засекаем время
        t = time()

        try:
            self.get_from_api()
        except Exception as e:
            print(e)
            self.status_code = 400 if self.status_code == 200 else 405

        print(time() - t)

        if self.securities:
            try:
                self.insert_to_database()
            except Exception as e:
                print(e)
                self.status_code = 301

        Thread(target=self.on_finish,
               args=(self.status_code, self.securities)).start()

    def insert_to_database(self):
        # Подключаемся к базе данных
        db = DatabaseInterface()
        db.connect_to_db()

        # Таблица, куда добавим цб
        table = SecuritiesInfoTable()

        # Сортируем по фиги
        self.securities.sort(key=lambda x: x.info.figi)

        # Получаем массив данных для добавления
        securities = [value.get_as_dict_security()
                      for value in self.securities]

        # Добавляем
        db.add_unique_data(
            table=table.get_table(),
            query=securities
        )

        # Получаем id только что добавленных цб
        # Отсортированных по фиги, что позволяет нам установить
        # соответствие между id цб и ее индексом в списке всех цб
        all_id = db.get_data_by_sql(
            {table.get_name(): [SecuritiesInfo.ID]},
            table.get_name(),
            sort_query=[f"{SecuritiesInfo.figi.value} ASC"]
        )

        # Ставим нужные id
        for i in range(len(self.securities)):
            self.securities[i].info.id = all_id[i][SecuritiesInfo.ID.value]

        # Парсим в массивы данные по конкретным видам цб
        bonds, stocks = [], []

        for sec in self.securities:
            if sec.security_type == SecurityType.BOND:
                bonds.append(sec.get_as_dict())
            else:
                stocks.append(sec.get_as_dict())

        # Добавляем в бд
        db.add_unique_data(
            table=StocksInfoTable().get_table(),
            query=stocks
        )

        db.add_unique_data(
            table=BondsInfoTable().get_table(),
            query=bonds
        )

        db.close_engine()

    def get_from_api(self):
        # Устанавливаем соединение
        with Client(self.__token) as client:
            try:
                # Загружаем все облигации
                bonds: list[tinkoffBond] = client.instruments.bonds(
                    instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL
                ).instruments

                # Создаем из них экземпляры нужного нам класса
                for loaded_instrument in bonds:
                    self.securities.append(
                        Bond(
                            class_code=loaded_instrument.class_code,
                            lot=loaded_instrument.lot,
                            currency=loaded_instrument.currency,
                            country=loaded_instrument.country_of_risk_name,
                            sector=loaded_instrument.sector,
                            security_type=SecurityType.BOND,
                            security_id=0,
                            figi=loaded_instrument.figi,
                            ticker=loaded_instrument.ticker,
                            security_name=loaded_instrument.name,

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
                            coupon=[]
                        )
                    )
            except RequestError as e:
                self.status_code = 402
                print(e)

            # Аналогично, но с акциями
            try:
                stocks: list[tinkoffShare] = client.instruments.shares(
                    instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL
                ).instruments

                for loaded_instrument in stocks:
                    self.securities.append(
                        Stock(
                            class_code=loaded_instrument.class_code,
                            lot=loaded_instrument.lot,
                            currency=loaded_instrument.currency,
                            country=loaded_instrument.country_of_risk_name,
                            sector=loaded_instrument.sector,
                            security_type=SecurityType.STOCK,
                            security_id=0,
                            figi=loaded_instrument.figi,
                            ticker=loaded_instrument.ticker,
                            security_name=loaded_instrument.name,

                            stock_id=-2,
                            ipo_date=loaded_instrument.ipo_date.date(),
                            issue_size=loaded_instrument.issue_size,
                            stock_type=StockType(loaded_instrument.share_type),
                            otc_flag=loaded_instrument.otc_flag,
                            div_yield_flag=loaded_instrument.div_yield_flag,
                            dividend=[]
                        )
                    )
            except RequestError as e:
                print(e)
                # Если ранее была ошибка, ставим код 404
                self.status_code = 403 if self.status_code != 402 else 404
