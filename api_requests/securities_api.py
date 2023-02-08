from abc import ABC
from datetime import datetime
from math import ceil, log10

import function
import threading

import sqlalchemy
import tinkoff.invest

from database.database_info import SecuritiesInfoTable, BondsInfoTable, \
    StocksInfoTable, CouponInfoTable, DividendInfoTable
from api_requests.security_getter import StandardQuery, SecurityGetter
from securities.securiries_types import SecurityType, StockType
from securities.securities import Security, Stock, Bond, SecurityInfo
from database.database_interface import DatabaseInterface

from tinkoff.invest.services import InstrumentIdType
from tinkoff.invest import Client, MoneyValue
from tinkoff.invest.exceptions import RequestError


def convert_money_value(data: MoneyValue):
    return data.units + data.nano / 10 ** ceil(log10(data.nano if data.nano > 0 else 1))


class GetSecurity(SecurityGetter, ABC, threading.Thread):
    security: Security | Bond | Stock | None = None
    add_to_other: bool
    status_code: int = 200

    def __init__(self, query: StandardQuery, on_finish: function, token: str, add_to_other=True, check_locally=True):
        super().__init__()
        self.query = query
        self.add_to_other = add_to_other
        self.on_finish = on_finish
        self.table = "securities_info"
        self.__token = token
        self.check_locally = check_locally

    def run(self) -> None:
        self.load_data()

        if self.security is not None:
            try:
                self.insert_to_database()
            except Exception as e:
                print(e)
                self.status_code = 301

        self.on_finish(self.status_code)

    def load_data(self):
        try:
            if self.check_locally:
                self.get_from_bd()
        except Exception as e:
            print(e)

        if self.security is None:
            self.get_from_api()

    def insert_to_database(self):
        table = SecuritiesInfoTable()
        db = DatabaseInterface()
        db.connect_to_db()

        if self.add_to_other:
            db.add_data(
                table.get_table(),
                values=self.security.get_as_database_value_security()
            )
            cursor: sqlalchemy.engine.cursor = db.execute_sql("SELECT MAX(ID) FROM " + table.get_name())

            for i in cursor:
                self.security.set_security_id(i[0])
                break

            if self.security.security_type == SecurityType.BOND or self.security.div_yield_flag:
                query = []

                if self.security.security_type == SecurityType.BOND:
                    sub_table = CouponInfoTable().get_table()
                    for values in self.security.coupon:
                        sub = {}
                        n = values.get_as_database_value()
                        for value in n:
                            if not (value.get_row_name() in ["ID", "UID"]):
                                sub[value.get_row_name()] = value.to_db_value()

                        query.append(sub)

                else:
                    sub_table = DividendInfoTable().get_table()
                    for values in self.security.dividend:
                        sub = {}
                        n = values.get_as_database_value()
                        for value in n:
                            if not (value.get_row_name() in ["ID", "UID"]):
                                sub[value.get_row_name()] = value.to_db_value()

                        query.append(sub)

                db.add_data(
                    sub_table,
                    query=query
                )

        if self.security.security_type == SecurityType.BOND:
            table = BondsInfoTable()
        elif self.security.security_type == SecurityType.STOCK:
            table = StocksInfoTable()

        db.add_data(
            table.get_table(),
            values=self.security.get_as_database_value()
        )

        cursor: sqlalchemy.engine.cursor = db.execute_sql("SELECT MAX(ID) FROM " + table.get_name())
        for i in cursor:
            self.security.set_id(i[0])
            break

    def get_from_bd(self):
        pass

    def get_from_api(self):
        data = self.query.get_query()

        with Client(self.__token) as client:
            r = client.instruments.find_instrument(query=data)
            result = r.instruments

            result.sort(key=lambda x: x.instrument_type != "share")

            if len(result) == 0:
                return

            self.query.security_info = SecurityInfo(-2, result[0].figi, result[0].ticker, result[0].name)

            loaded_instrument: tinkoff.invest.Share | tinkoff.invest.Bond
            sub_data: list[tinkoff.invest.Dividend | tinkoff.invest.Coupon] | None = None

            try:
                if result[0].instrument_type == "bond":
                    loaded_instrument = client.instruments.bond_by(
                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                        id=result[0].figi
                    ).instrument
                    if self.add_to_other:
                        self.table = "bonds_info"

                    sub_data = client.instruments.get_bond_coupons(
                        figi=loaded_instrument.figi,
                        from_=datetime(year=1970, month=1, day=1),
                        to=datetime(year=2100, month=1, day=1)
                    ).events

                elif result[0].instrument_type == "share":
                    loaded_instrument: tinkoff.invest.Share = client.instruments.share_by(
                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                        id=result[0].figi
                    ).instrument
                    if self.add_to_other:
                        self.table = "stocks_info"

                    if loaded_instrument.div_yield_flag:
                        sub_data = client.instruments.get_dividends(
                            figi=loaded_instrument.figi,
                            from_=datetime(year=1990, month=1, day=1),
                            to=datetime(year=2100, month=1, day=1)
                        ).dividends
                else:
                    return

                if not len(sub_data):
                    sub_data = None

                c = 0

                if result[0].instrument_type == "bond":
                    c = 1

                self.security = Security(
                    loaded_instrument.class_code,
                    loaded_instrument.lot,
                    loaded_instrument.currency,
                    loaded_instrument.country_of_risk,
                    loaded_instrument.sector,
                    SecurityType(c),
                    -2,
                    loaded_instrument.figi,
                    loaded_instrument.ticker,
                    loaded_instrument.name
                )

                if self.add_to_other:
                    if self.security.security_type == SecurityType.BOND:
                        self.security = Bond(
                            self.security,
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
                            [
                                sub_data,
                                -2,
                                -2
                            ]
                        )
                    elif self.security.security_type == SecurityType.STOCK:
                        self.security = Stock(
                            self.security,
                            [
                                -2,
                                loaded_instrument.ipo_date.date(),
                                loaded_instrument.issue_size,
                                StockType(loaded_instrument.share_type),
                                loaded_instrument.otc_flag,
                                loaded_instrument.div_yield_flag
                            ],
                            [
                                sub_data,
                                -2,
                                -2
                            ]
                        )

            except RequestError as e:
                print(e)
                self.status_code = 400

            print(loaded_instrument)
            print(sub_data)
