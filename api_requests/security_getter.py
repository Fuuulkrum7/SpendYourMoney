from abc import ABC, abstractmethod

import function

from securities.securities import SecurityInfo


class StandardQuery:
    security_info: SecurityInfo
    query_text: str

    def __init__(self, info: SecurityInfo, query_text: str):
        self.security_info = info
        self.query_text = query_text

    def get_query(self) -> str:
        if self.security_info.figi:
            return self.security_info.figi
        if self.security_info.ticker:
            return self.security_info.ticker
        if self.security_info.name:
            return self.security_info.name
        return self.query_text


class SecurityGetter(ABC):
    table: str
    query: StandardQuery
    check_locally: bool
    insert_to_db: bool
    on_finish: function = None

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def insert_to_database(self):
        pass

    @abstractmethod
    def get_from_bd(self):
        pass

    @abstractmethod
    def get_from_api(self):
        pass
