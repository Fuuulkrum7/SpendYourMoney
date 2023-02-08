import sqlalchemy
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
        a = str(self.__value)
        if isinstance(self.__value, bool):
            return a.lower()
        return a

    def to_db_value(self):
        if isinstance(self.__value, bool):
            return self.get_value()
        return str(self.__value)

    def __eq__(self, other):
        if not isinstance(other, DatabaseValue):
            return False
        if self.get_row_name() == other.get_row_name() and self.get_value() == other.get_value():
            return True
        return False

    def get_row_name(self) -> str:
        return self.__row.name

    def get_type(self) -> str:
        return str(self.__row.value)

    def get_value(self):
        return self.__value

    def get_row(self):
        return self.__row


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

    def connect_to_db(self):
        try:
            self.__engine = sqlalchemy.create_engine("mysql+pymysql://root:0urSh!TtyD8@localhost/" + self.info["name"])

            if not database_exists(self.__engine.url):
                print("it's ok, we're just creating db")
                self.create_database()

                self.connected = 1
        except Exception as e:
            print(e)
            self.connected = -1

    def add_data(self, table: Base, query: list[dict] = None, values: list[DatabaseValue] = None):
        if query is None and values is None:
            return

        if query is None:
            query = {}
            for value in values:
                if not (value.get_row_name() in ["ID", "UID"]):
                    query[value.get_row_name()] = value.to_db_value()

        with self.__engine.connect() as conn:
            conn.execute(
                sqlalchemy.insert(table),
                query
            )

    def add_unique_data(self, rows: list[DatabaseValue]):
        pass

    # Альтернативный вариант получения данных путем создания запроса sql
    def get_data_by_sql(self, rows: list[Enum], table: str,
                        where: dict = None, sort_query: list[list[Enum, str]] = None) -> list[list[DatabaseValue]]:
        query = f"SELECT "

        if rows:
            for row in rows:
                query += f"{row.name} "
        else:
            query += "*"

        query += f" FROM {table}"

        if where is not None:
            query += " WHERE "
            d = " AND " if len(where) > 1 else ""
            i = 0
            for key, value in where:
                query += f"{key} = {value}"
                query += d if i < len(where) - 1 else ""
                i += 1

        if sort_query is not None:
            query += " ORDER BY "
            i = 0
            for row in sort_query:
                query += f"{row[0].name} {row[1]}"
                query += ", " if i < len(where) - 1 else ""
                i += 1

        with self.__engine.connect() as conn:
            result = conn.execute(query)
            values: list[list[DatabaseValue]] = []

            for r in result:
                value: list[DatabaseValue] = []
                for row in rows:
                    val = r[row.name]
                    if row.value == "INT":
                        val = int(val)
                    elif row.value == "BOOL":
                        val = val.lower() == "true"
                    elif row.value == "DOUBLE":
                        val = float(val)

                    value.append(DatabaseValue(row, val))
                values.append(value)

            return values

    def clear_db(self):
        try:
            self.__engine.execute("DROP DATABASE " + self.info["name"] + ";")
        except Exception as e:
            print(e)
            self.connected = -2
        self.connected = 0

    def drop_table(self) -> int:
        pass

    def check_connection(self):
        return self.connected

    def create_database(self):
        scripts = FileLoader.get_file(self.__path + "/info/files/init.sql", datatype=str)

        self.__engine.execute("CREATE DATABASE " + self.info["name"])
        self.__engine.execute("USE " + self.info["name"])

        scripts = list(filter(len, scripts.replace("\n", "").split(";")))
        with self.__engine.connect() as conn:
            for script in scripts:
                conn.execute(script)

    def execute_sql(self, sql: str):
        with self.__engine.connect() as conn:
            return conn.execute(sql)
