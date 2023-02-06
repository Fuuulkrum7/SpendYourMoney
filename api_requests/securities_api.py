from abc import ABC

import function
import threading
from pandas import DataFrame

from api_requests.security_getter import StandardQuery, SecurityGetter
from securities.securities import Security, Stock, Bond, SecurityInfo

from tinkoff.invest.services import InstrumentsService, InstrumentIdType
from tinkoff.invest import Client
from tinkoff.invest.exceptions import RequestError


class GetSecurity(SecurityGetter, ABC, threading.Thread):
    security: Security = None
    add_to_other: bool

    def __init__(self, query: StandardQuery, on_finish: function, token: str, add_to_other=True):
        super().__init__()
        self.query = query
        self.add_to_other = add_to_other
        self.on_finish = on_finish
        self.__token = token

    def run(self) -> None:
        self.load_data()

        if self.security is not None:
            self.insert_to_database()

        self.on_finish()

    def load_data(self):
        self.get_from_bd()

        if self.security is None:
            self.get_from_api()

    def insert_to_database(self):
        pass

    def get_from_bd(self):
        pass

    def get_from_api(self):
        data = self.query.get_query()

        with Client(self.__token) as client:
            r = client.instruments.find_instrument(query=data)
            result = r.instruments

            if len(result) == 0:
                return

            self.query.security_info = SecurityInfo(-2, result[0].figi, result[0].ticker, result[0].name)

            loaded_instrument: InstrumentsService
            try:
                if result[0].instrument_type == "bond":
                    loaded_instrument = client.instruments.bond_by(
                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                        id=result[0].figi
                    )
                elif result[0].instrument_type == "share":
                    loaded_instrument = client.instruments.share_by(
                        id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                        id=result[0].figi
                    )
                else:
                    return
            except RequestError as e:
                print(e)

            print(loaded_instrument)
