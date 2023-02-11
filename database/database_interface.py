import os

from sqlalchemy.engine.base import Engine
from sqlalchemy_utils import database_exists

from database.database_info import *
from info.file_loader import FileLoader


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

    def add_data(self, table: Base, query: list[dict] = None, values: dict = None):
        if query is None and values is None:
            return

        if query is None:
            query = [dict(filter(lambda x: not (x[0] in "UID"), values.items()))]

        with self.__engine.connect() as conn:
            conn.execute(
                sqlalchemy.insert(table),
                query
            )

    def add_unique_data(self, table: Base, query: list[dict] = None, values: dict = None):
        pass

    # Альтернативный вариант получения данных путем создания запроса sql
    def get_data_by_sql(self, rows: dict[str, list[Enum]], table: str, where: str = "",
                        sort_query: list[str] = None, join: str = "") -> list[dict]:
        query = f"SELECT "

        i = 0
        for key, row in rows.items():
            tbl = ""
            if len(rows) > 1:
                tbl = key + "."
            query += ", ".join(map(lambda x: f"{tbl}{x.name}", row))

            i += 1
            if i < len(rows):
                query += ", "

        query += f" FROM {table}"

        if join:
            query += f" INNER JOIN {join}"

        if where:
            query += f" {where}"

        if sort_query is not None:
            query += " ORDER BY "
            i = 0
            for row in sort_query:
                query += row
                query += ", " if i < len(sort_query) - 1 else ""
                i += 1

        with self.__engine.connect() as conn:
            result = conn.execute(query)
            values: list[dict] = []

            for r in result:
                value: dict = {}
                for sub_row in rows.values():
                    for row in sub_row:
                        value[row.name] = r[row.name]
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
        scripts = list(filter(len, scripts.replace("\n", "").split(";")))

        self.__engine = sqlalchemy.create_engine("mysql+pymysql://root:0urSh!TtyD8@localhost")

        with self.__engine.connect() as conn:
            conn.execute("commit")
            conn.execute("CREATE DATABASE " + self.info["name"])
            conn.execute("USE " + self.info["name"])

            for script in scripts:
                conn.execute(script)

    def execute_sql(self, sql: str):
        with self.__engine.connect() as conn:
            return conn.execute(sql)
