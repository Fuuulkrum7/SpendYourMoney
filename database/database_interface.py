import os
from platform import system

from sqlalchemy.engine.base import Engine
from sqlalchemy import text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.sql import ColumnCollection
from sqlalchemy_utils import database_exists

from database.database_info import *
from info.file_loader import FileLoader


class DatabaseInterface:
    """
    Класс, отвечающий за прямую работу с бд. Запускать в отдельном потоке.
    """
    __engine: Engine = None
    # 0 - ещё не подключена
    # 1 - успешно подключена
    # -1 - подключение закончилось ошибкой
    connected: int = 0
    __path: str
    # Информация о базе данных
    info: dict
    library = "pymysql"
    version: int = 1

    def __init__(self):
        sep = "\\" if system() == "Windows" else "/"
        # Получаем путь до папки, где лежит файл
        folder = os.path.abspath("database_interface.py").split(sep)
        # Удаляем папку, где лежит файл, из пути
        folder.pop()
        # Сохраняем его
        self.__path = sep.join(folder)

        # загружаем данные по бд общие
        info = FileLoader.get_json(self.__path +
                                   "/info/files/.database_info.json")
        # Если файла нет, значит, пользователь идиот и его удалил
        if info is None:
            raise FileNotFoundError
        # Сохраняем инфу
        self.info = info

        try:
            version = FileLoader.get_file(
                self.__path + "/info/files/.db_version",
                datatype=int
            )

            if version is not None:
                version = int(version, 16)
                self.version = int(version ** (1 / 8)) - 1
            else:
                print("pre-alpha db found")
        except ValueError:
            print("file changed")

    def connect_to_db(self):
        try:
            # Подключаемся к бд
            self.__engine = \
                sqlalchemy.create_engine(
                    f"mysql+{self.library}://{self.info['username']}:"
                    f"{self.info['password']}@localhost/"
                    f"{self.info['name']}"
                )

            if self.version != self.info["version"]:
                print("old db found")
                self.migrate()

                version = (self.info["version"] + 1) ** 8
                FileLoader.save_file(
                    self.__path + "/info/files/.db_version",
                    [hex(version)[2:]]
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
        if query is None and values is None or not query and not values:
            return

        # Если тело запроса не пустое, фильтруем на всякий случай
        # С защитой от id
        if query is None and ("UID" in values or "ID" in values):
            query = [dict(filter(
                lambda x: not (x[0] in ["UID", "ID"]), values.items()
            ))]
        elif query and ("UID" in query[0] or "ID" in query[0]):
            query = [dict(filter(
                lambda x: not (x[0] in ["UID", "ID"]), val.items()
            )) for val in query]

        # Подсоединяемся к бд и добавляем данные
        with self.__engine.connect() as conn:
            insrt = insert(table).values(query)

            columns = {}
            for key, item in insrt.inserted.items():
                if not (key in ["ID", "UID"]):
                    columns[key] = item

            on_duplicate = insrt.on_duplicate_key_update(
                **columns
            )

            conn.execute(
                on_duplicate
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

    # Миграция со старо версии бд
    def migrate(self):
        # В случае со совсем старыми было очень много изменений
        # проще все снести
        if self.version < 4:
            self.clear_db()
            return
        # Если версия 4
        if self.version == 4:
            try:
                # Добавляем столбец с приоритетом
                self.__engine.execute(
                    text(
                        f"ALTER TABLE {SecuritiesInfoTable.__tablename__} "
                        f"ADD {SecuritiesInfo.PRIORITY.value} "
                        f"TINYINT DEFAULT 0"
                    )
                )
            except Exception as e:
                print(e)
                return

            # Получаем массив всех цб
            table = SecuritiesInfoTable().get_name()
            data = self.get_data_by_sql(
                {
                    table: [
                        SecuritiesInfo.FIGI, SecuritiesInfo.ID
                    ]
                },
                table
            )
            # Если бд пуста, то ничего не добавляем
            if not data:
                return

            # Получаем массив фиги приоритетных
            figis = FileLoader.get_file(self.__path +
                                        "/info/files.priority_figis.txt")

            # Делаем апдейт всех цб в базе данных
            query = f"UPDATE {SecuritiesInfoTable.__tablename__} " \
                    f"SET {SecuritiesInfo.PRIORITY.value} = CASE \n"

            # Ставим условие, когда какой приоритет ставить
            for val in data:
                query += f"WHEN {SecuritiesInfo.ID.value} = "
                query += f" {val[SecuritiesInfo.ID.value]} THEN "
                query += f"{int(val[SecuritiesInfo.FIGI.value] in figis)}\n"

            query += "ELSE 0\n END;"

            # Выполняем запрос
            self.execute_sql(query)
        # Если версия 5 и ниже
        if self.version <= 5:
            try:
                # Delete old constraint keys
                self.__engine.execute(
                    text(f"ALTER TABLE {DividendInfoTable.__tablename__} "
                         f"DROP CONSTRAINT UC_div")
                )
                self.__engine.execute(
                    text(f"ALTER TABLE {CouponInfoTable.__tablename__} "
                         f"DROP CONSTRAINT UC_div")
                )

                # Create new constraint keys
                self.__engine.execute(
                    text(f"ALTER TABLE {CouponInfoTable.__tablename__} "
                         f"ADD CONSTRAINT UC_coup "
                         f"UNIQUE(security_id, coupon_date)")
                )
                self.__engine.execute(
                    text(f"ALTER TABLE {DividendInfoTable.__tablename__} "
                         f"ADD CONSTRAINT UC_div "
                         f"UNIQUE (security_id, declared_date, div_value)")
                )
            except Exception as e:
                print(e)
                return

    def clear_db(self):
        try:
            # Если версия выше 3, то сносим лишь часть таблиц
            if self.version >= 3:
                scripts = FileLoader.get_file(
                    self.__path + "/info/files/delete.sql",
                    datatype=str
                ).replace("\n", "").split(";")

                # удаляем пустые элементы
                scripts = list(filter(len, scripts))

                # Загружаем скрипты для удаления таблиц
                create = FileLoader.get_file(
                    self.__path + "/info/files/init.sql"
                )

                # Удаляем и создаем таблицы
                for deleter in scripts:
                    self.__engine.execute(text(deleter))
                for creator in create:
                    self.__engine.execute(text(creator))

            else:
                # Если версия старовата, то удаляем бд
                self.__engine.execute(f"DROP DATABASE {self.info['name']};")
        except Exception as e:
            print(e)
            # Если ошибка была, отмечаем это
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
            f"mysql+{self.library}://{self.info['username']}:"
            f"{self.info['password']}@localhost"
        )

        with self.__engine.connect() as conn:
            conn.execute("commit")
            conn.execute("CREATE DATABASE " + self.info["name"])
            conn.execute("USE " + self.info["name"])

            for script in scripts:
                conn.execute(text(script))

            conn.close()

    def execute_sql(self, sql: str):
        with self.__engine.connect() as conn:
            return conn.execute(sql)

    def close_engine(self):
        self.__engine.dispose()
