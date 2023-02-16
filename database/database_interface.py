import os
from platform import system

from sqlalchemy.engine.base import Engine
from sqlalchemy import text
from sqlalchemy.dialects.mysql import insert, Insert
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
        sep = "\\" if system() == "Windows" else "/"
        # Получаем путь до папки, где лежит файл
        folder = os.path.abspath("database_interface.py").split(sep)
        # Удаляем папку, где лежит файл, из пути
        folder.pop()
        # Сохраняем его
        self.__path = "/".join(folder)

        # загружаем данные по бд общие
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
                    f"mysql+mysqldb://{self.info['username']}:"
                    f"{self.info['password']}@localhost/"
                    f"{self.info['name']}"
                )

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
                insert(table),
                query
            )
            conn.close()

    def add_unique_data(self, table: Base, query: list[dict] = None,
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
            insrt = insert(table).prefix_with("IGNORE").values(query)

            conn.execute(
                insrt
            )
            conn.close()

    # вариант получения данных путем создания запроса sql
    def get_data_by_sql(self, rows: dict[str, list[Enum]],
                        table: str, where: str = "",
                        sort_query: list[str] = None,
                        join: str = "", params: dict = {}) -> list[dict]:
        """
        :param params:
        :param rows: Столбцы, по которым будет проводиться выборка. В случае
        использования join требуется указать имя таблицы, из которой берутся
        данные столбцы.
        :param table: Основная таблица, из которой ведется выборка.
        :param where: Параметр-условие, по которому ведется выборка.
        Для join использовать ON.
        :param sort_query: Сортировка по какому элементу.
        :param join: Для объединения двух таблиц в запросе.
        :return: Возвращаем данные, которые уже спарсили, используя имена
        столбцов.
        """
        # Начинаем формировать запрос
        query = f"SELECT "

        # Перебираем столбцы
        i = 0
        for key, row in rows.items():
            # По умолчанию имени таблицы нет
            tbl = ""
            # Если у нас несколько таблиц, указываем их имена
            if len(rows) > 1:
                tbl = key + "."
            # Формируем строку
            query += ", ".join(map(lambda x: f"{tbl}{x.value}", row))

            i += 1
            # Если не последняя строка таблицы, добавляем запятую
            if i < len(rows):
                query += ", "

        # Основная таблица
        query += f" FROM {table}"

        # Если данные в join есть, добавляем их
        if join:
            query += f" INNER JOIN {join}"

        # Если надо указать условие выборки, делаем это
        if where:
            query += f" {where}"

        # Если сортировка не пустая, формируем ее
        if sort_query is not None:
            query += " ORDER BY "
            query += ", ".join(sort_query)

        query = text(query)

        # Подключаемся к бд
        with self.__engine.connect() as conn:
            # Делаем запрос
            result = conn.execute(query, **params)
            values: list[dict] = []

            # Перебираем полученные данные
            for r in result:
                # Формируем словарь из пар имя столбца - значение
                value: dict = {}
                for sub_row in rows.values():
                    for row in sub_row:
                        value[row.value] = r[row.value]
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

        self.__engine = sqlalchemy.create_engine(
            f"mysql+mysqldb://{self.info['username']}:"
            f"{self.info['password']}@localhost"
        )

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
