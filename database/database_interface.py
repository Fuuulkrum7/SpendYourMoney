import os

from sqlalchemy.engine.base import Engine
from sqlalchemy_utils import database_exists

from database.database_info import *
from info.file_loader import FileLoader


class DatabaseInterface:
    """
    Класс, отвечающий за прямую работу с бд. Запускать в отдельном потоке.
    """
    __engine: Engine = None
    connected: int = 0
    __path: str
    info: dict

    def __init__(self):
        # Получаем путь до папки, где лежит файл
        folder = os.path.abspath("database_interface.py").split("/")
        # Удаляем папку, где лежит файл, из пути
        folder.pop()
        # Сохраняем его
        self.__path = "/".join(folder)

        # загружаем данные по бд общие
        print(__path)
        info = FileLoader.get_json(self.__path +
                                   "/info/files/.database_info.json")
        # Если файла нет, значит, пользователь идиот и его удалил
        if info is None:
            raise FileNotFoundError
        # Сохраняем инфу
        self.info = info

    def connect_to_db(self):
        try:
            # Подключаемся к бд
            self.__engine = \
                sqlalchemy.create_engine(
                    f"mysql+pymysql://root:0urSh!TtyD8@localhost/"
                    f"{self.info['name']}")

            # Если бд не существует, создаем
            if not database_exists(self.__engine.url):
                print("it's ok, we're just creating db")
                self.create_database()

                # Говорим, что все подключено
                self.connected = 1
        except Exception as e:
            print(e)
            self.connected = -1

    def add_data(self, table: Base, query: list[dict] = None,
                 values: dict = None):
        # Если вообще данных для добавления нет
        if query is None and values is None:
            return

        # Если тело запроса не пустое, фильтруем на всякий случай
        if query is None:
            query = [dict(filter(
                lambda x: not (x[0] in ["UID", "ID"]), values.items()
            ))]
        else:
            query = [dict(filter(
                lambda x: not (x[0] in ["UID", "ID"]), val.items()
            )) for val in query]

        # Подсоединяемся к бд и добавляем данные
        with self.__engine.connect() as conn:
            conn.execute(
                sqlalchemy.insert(table),
                query
            )
            conn.close()

    def add_unique_data(self, table: Base,
                        query: list[dict] = None, values: dict = None):
        pass

    # вариант получения данных путем создания запроса sql
    def get_data_by_sql(self, rows: dict[str, list[Enum]],
                        table: str, where: str = "",
                        sort_query: list[str] = None,
                        join: str = "") -> list[dict]:
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
            query += ", ".join(sort_query)

        with self.__engine.connect() as conn:
            result = conn.execute(query)
            values: list[dict] = []

            for r in result:
                value: dict = {}
                for sub_row in rows.values():
                    for row in sub_row:
                        value[row.name] = r[row.name]
                values.append(value)

            conn.close()
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
        scripts = FileLoader.get_file(self.__path + "/info/files/init.sql",
                                      datatype=str)
        scripts = list(filter(len, scripts.replace("\n", "").split(";")))

        self.__engine = sqlalchemy.create_engine\
            ("mysql+pymysql://root:0urSh!TtyD8@localhost")

        with self.__engine.connect() as conn:
            conn.execute("commit")
            conn.execute("CREATE DATABASE " + self.info["name"])
            conn.execute("USE " + self.info["name"])

            for script in scripts:
                conn.execute(script)

            conn.close()

    def execute_sql(self, sql: str):
        with self.__engine.connect() as conn:
            return conn.execute(sql)

    def close_engine(self):
        self.__engine.dispose()
