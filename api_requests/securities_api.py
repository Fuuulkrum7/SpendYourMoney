from abc import ABC
from datetime import datetime

import function
import threading

import tinkoff.invest

from api_requests.security_getter import StandardQuery, SecurityGetter
from securities.securiries_types import SecurityType, StockType
from securities.securities import Security, Stock, Bond, SecurityInfo
from database.database_interface import DatabaseInterface

from tinkoff.invest.services import InstrumentIdType
from tinkoff.invest import Client
from tinkoff.invest.exceptions import RequestError


class GetSecurity(SecurityGetter, ABC, threading.Thread):
    security: Security = None
    add_to_other: bool

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
            self.insert_to_database()

        self.on_finish()

    def load_data(self):
        if self.check_locally:
            self.get_from_bd()

        if self.security is None:
            self.get_from_api()

    def insert_to_database(self):
        db = DatabaseInterface()
        db.connect_to_db()
        db.add_data(
            self.security.get_as_database_value()
        )

    def get_from_bd(self):
        pass

    def get_from_api(self):
        data = self.query.get_query()

        with Client(self.__token) as client:
            r = client.instruments.find_instrument(query=data)
            result = r.instruments

            result.sort(key=lambda x: x.instrument_type != "share")
            # print(*result, sep='\n')
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

                    if not len(sub_data):
                        sub_data = None

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
                            from_=datetime(year=1970, month=1, day=1),
                            to=datetime(year=2100, month=1, day=1)
                        ).dividends
                else:
                    return

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

            print(loaded_instrument)
            print(sub_data)
