from enum import Enum
from sqlalchemy import create_engine, Engine
from info.file_loader import FileLoader
from sqlalchemy_utils import database_exists, create_database
import os
import asyncio


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
    table_name: str
    __database: Engine = None

    def __init__(self, table_name: str):
        self.table_name = table_name

        asyncio.run(self.__connect_to_db())

    async def __connect_to_db(self):
        folder = os.path.abspath("database_interface.py").split("/")
        folder.pop()
        folder = "/".join(folder)

        info = FileLoader.get_json(folder + "/info/files/.database_info.json")
        if info is None:
            raise FileNotFoundError
        name = info["name"]

        try:
            self.__database = create_engine("mysql+pymysql://user:password@localhost/" + name)

            if not database_exists(self.__database.url):
                create_database(self.__database.url)
        except Exception as e:
            print(e)
            # raise e
        # TODO change

    async def add_data(self, values: list[DatabaseValue]):
        pass

    async def add_unique_data(self, rows: list[DatabaseValue]):
        pass

    async def get_data(self, rows: list[Enum]) -> list[DatabaseValue]:
        pass

    async def clear_db(self) -> int:
        pass

    async def drop_table(self) -> int:
        pass
