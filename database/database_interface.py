from enum import Enum
import sqlalchemy


class DatabaseValue:
    __row: Enum = None
    __value: object = None

    def __init__(self, row: Enum, value):
        self.__value = value
        self.__row = row

    def __str__(self):
        return str(self.__value)

    def get_row_name(self) -> str:
        return self.__row.name

    def get_type(self) -> str:
        return str(self.__row.value)

    def get_value(self) -> object:
        return self.__value


class DatabaseInterface:
    db_name: str = ""
    table_name: str = ""

    def __init__(self, db_name: str, table_name: str):
        self.db_name = db_name
        self.table_name = table_name

    def add_data(self, values: list[DatabaseValue]):
        pass

    def add_unique_data(self, rows: list[DatabaseValue]):
        pass

    def get_data(self, rows: list[Enum]) -> list[DatabaseValue]:
        pass

    def clear_db(self) -> int:
        pass

    def drop_table(self) -> int:
        pass
