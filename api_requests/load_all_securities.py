from time import time

import function
import sqlalchemy
from threading import  Thread
from tinkoff.invest import Client, RequestError, Share as tinkoffShare, \
    Bond as tinkoffBond, InstrumentStatus

from database.database_info import SecuritiesInfoTable, BondsInfoTable, \
    StocksInfoTable, SecuritiesInfo
from database.database_interface import DatabaseInterface
from securities.securiries_types import SecurityType, StockType
from securities.securities import Bond, Stock


class LoadAllSecurities(Thread):
    # Список цб
    securities: list[Bond or Stock] = []
    # Интересно, что же это такое... Даже не знаю
    status_code: int = 200

    def __init__(self, on_finish: function, token: str):
        super().__init__()

        self.on_finish = on_finish
        self.__token = token

    # Тут все банально
    def run(self) -> None:
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

        self.on_finish(self.status_code)

    def insert_to_database(self):
        # Подключаемся к базе данных
        db = DatabaseInterface()
        db.connect_to_db()

        table = SecuritiesInfoTable()

        self.securities.sort(key=lambda x: x.info.figi)

        securities = [value.get_as_dict_security()
                      for value in self.securities]

        db.add_unique_data(
            table=table.get_table(),
            query=securities
        )

        all_id = db.get_data_by_sql(
            {table.get_name(): [SecuritiesInfo.ID]},
            table.get_name(),
            sort_query=[f"{SecuritiesInfo.figi.value} ASC"]
        )

        for i in range(len(self.securities)):
            self.securities[i].info.id = all_id[i][SecuritiesInfo.ID.value]

        bonds, stocks = [], []

        for sec in self.securities:
            if sec.security_type == SecurityType.BOND:
                bonds.append(sec.get_as_dict())
            else:
                stocks.append(sec.get_as_dict())

        db.add_unique_data(
            table=StocksInfoTable().get_table(),
            query=stocks
        )

        db.add_unique_data(
            table=BondsInfoTable().get_table(),
            query=bonds
        )

    def get_from_api(self):
        with Client(self.__token) as client:
            try:
                bonds: list[tinkoffBond] = client.instruments.bonds(
                    instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL
                ).instruments

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
                self.status_code = 403 if self.status_code != 402 else 404
