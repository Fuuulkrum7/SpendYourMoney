from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy_utils import database_exists
from info.file_loader import FileLoader
import os

from database.database_info import *


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
    __engine: Engine = None
    connected: int = 0
    __path: str
    info: dict

    def __init__(self):
        folder = os.path.abspath("database_interface.py").split("/")
        folder.pop()
        self.__path = "/".join(folder)

        info = FileLoader.get_json(self.__path + "/info/files/.database_info.json")
        if info is None:
            raise FileNotFoundError
        self.info = info

    async def connect_to_db(self):
        try:
            self.__engine = create_engine("mysql+pymysql://root:0urSh!TtyD8@localhost/" + self.info["name"])

            self.clear_db()

            if not database_exists(self.__engine.url):
                print("it's ok, we're just creating db")
                await self.create_database()

                self.connected = 1
        except Exception as e:
            print(e)
            self.connected = -1

    async def add_data(self, values: list[DatabaseValue]):
        pass

    async def add_unique_data(self, rows: list[DatabaseValue]):
        pass

    async def get_data(self, rows: list[Enum]) -> list[DatabaseValue]:
        pass

    def clear_db(self):
        try:
            self.__engine.execute("DROP DATABASE " + self.info["name"] + ";")
        except Exception as e:
            print(e)
            self.connected = -2
        self.connected = 0

    async def drop_table(self) -> int:
        pass

    def check_connection(self):
        return self.connected

    async def create_database(self):
        script = FileLoader.get_file(self.__path + "/info/files/init.sql", datatype=str)

        self.__engine.execute("CREATE DATABASE " + self.info["name"])
        self.__engine.execute("USE " + self.info["name"])
        self.__engine.execute(script)
