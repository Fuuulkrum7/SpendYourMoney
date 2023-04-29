import hashlib
from PyQt5.QtCore import QThread as Thread, pyqtSignal

import sqlalchemy
import tinkoff.invest
from tinkoff.invest import Client, RequestError

from database.database_info import UserTableSQLAlchemy, UserTable
from database.database_interface import DatabaseInterface
from info.user import User


class CheckUser(Thread):
    """
    class for checking user data. codes:
    1** - problems with userdata
    100 - login exists, but password is incorrect
    2** - success
    200 - user exists in db and remotely. full success
    201 - user exists locally, but remotely we did not check
    202 - locally does not exist, remotely - yes
    211 - locally ok, remotely - error
    250 - no data locally, remotely - did not check
    3**
    300 - error occurred, remotely did not check
    4**
    400 - remotely no user
    5**
    complete nightmare
    """
    # Пароль
    password: str
    # Логин
    login: str
    # Заготовка под пользователя
    user: User = None
    # Статус-код, см выше
    status_code: int = 201
    data_downloaded = pyqtSignal(object)

    def __init__(self, login: str, password: str, on_finish, token: str = ""):
        super().__init__()
        # Пароль хешируем
        self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        self.login = login
        self.__token = token
        self.data_downloaded.connect(on_finish)

    def run(self) -> None:
        try:
            # Подключаемся к бд
            db = DatabaseInterface()
            db.connect_to_db()

            # Таблица, откуда берем данные
            table = UserTableSQLAlchemy()

            # Делаем запрос нужных таблиц. Ищем по совпадению логина
            result = db.get_data_by_sql(
                {table.get_name(): [UserTable.UID, UserTable.token,
                                    UserTable.username, UserTable.access_level,
                                    UserTable.status, UserTable.password]},
                table.get_name(),
                where=f" WHERE {UserTable.username.value} = '{self.login}' "
            )

            # Если данные по пользователю есть
            if result:
                result = result[0]

                # Проверяем пароль
                if result[UserTable.password.value] == self.password:
                    # Удаляем поле с паролем
                    result.pop("password")

                    # Создаем пользователя из данных
                    self.user = User(**result)
                    # Записываем токен
                    self.__token = self.user.get_token()
                # Если пользователь имеет другой пароль, отмечаем это
                else:
                    self.status_code = 100
            # Если пользователя нет, отмечаем
            else:
                self.status_code = 250
        # В случае ошибки при обращении к бд, отмечаем, что не получилось
        # обратиться к бд
        except Exception as e:
            print(e)
            self.status_code = 300

        # Если токен есть (был передан или загружен в поиске пользователя)
        if self.__token:
            # Создаем подключение
            with Client(self.__token) as client:
                try:
                    # Получаем массив аккаунтов
                    result = client.users.get_accounts().accounts

                    # Смотрим, нормальные ли права у токена и все ли
                    # в порядке с аккаунтом (не закрыт ли он)
                    result = list(filter(
                        lambda x: x.status != tinkoff.invest.AccountStatus.
                        ACCOUNT_STATUS_CLOSED and x.access_level != tinkoff.
                        invest.AccessLevel.ACCOUNT_ACCESS_LEVEL_NO_ACCESS,
                        result
                    ))

                    # Если ни одного нормального аккаунта нет
                    if not len(result):
                        # 500 если до этого про пользователя мы ничего не
                        # узнали, иначе 400
                        self.status_code = 500 if self.status_code >= 300 \
                            else 400
                    else:
                        # Иначе меняем статус-код
                        result = result[0]
                        self.status_code = 200 if self.status_code == 201 \
                            else 202
                        # И парсим пользователя
                        self.user = User(
                            token=self.__token,
                            username=self.login,
                            access_level=result.access_level,
                            status=result.status,
                            user_id=0
                        )
                # В случае ошибки
                except RequestError as e:
                    print(e)
                    self.status_code = 500 if self.status_code >= 250 \
                        else 211

        # Thread(target=self.on_finish, args=(self.status_code, self.user)).\
        #     start()
        self.data_downloaded.emit((self.status_code, self.user))

    def get_user(self):
        return self.user


class CreateUser(Thread):
    """
    status-codes
    1** - some userdata exists
    110 - user exists
    101 - login exists, password is incorrect
    102 - invalid token.
    2**
    200 - success
    3**
    300 - error with db
    5**
    500 - complete nightmare
    """
    user: User = None
    status_code: int = 200
    password: str
    data_downloaded = pyqtSignal(object)

    def __init__(self, user: User, password: str, on_finish):
        super().__init__()

        self.check = None
        self.user = user
        self.password = password
        self.data_downloaded.connect(on_finish)

    def run(self) -> None:
        # Запускаем проверку пользователя
        self.check: CheckUser = CheckUser(
            self.user.username,
            self.password,
            on_finish=self.on_finish,
            token=self.user.get_token()
        )
        self.check.start()

    def on_finish(self):
        code = self.check.status_code

        # Все ок, создаем пользователя
        if code == 202:
            try:
                # Получаем пользователя из метода по проверке
                self.user = self.check.get_user()

                # Подключаемся к бд
                db = DatabaseInterface()
                db.connect_to_db()

                # Парсим в словарь
                query = self.user.get_as_dict()
                # Добавляем поле пароль
                query["password"] = \
                    hashlib.sha512(
                        self.password.encode('utf-8')).hexdigest()

                # Добавляем данные в таблицу
                table = UserTableSQLAlchemy()
                db.add_data(
                    table=table.get_table(),
                    values=query
                )

                cursor: sqlalchemy.engine.cursor = \
                    db.execute_sql(
                        "SELECT MAX(UID) FROM " + table.get_name())

                # Получаем id и обновляем индекс пользователя
                for val in cursor:
                    self.user.set_uid(val[0])
                    break

                # Отключаемся от бд
                db.close_engine()
            except Exception as e:
                print(e)
                self.status_code = 300
        # пользователь уже есть
        elif code in [200, 211]:
            self.status_code = 110
        # Такой логин уже есть
        elif code == 100:
            self.status_code = 101
        # кривой токен/его вообще нет
        elif code in [400, 201, 300, 301]:
            self.status_code = 102
        # Ошибка необрабатываемая
        else:
            self.status_code = 500

        # Запускаем поток
        self.data_downloaded.emit((self.status_code, self.user))

    def get_user(self):
        return self.user
