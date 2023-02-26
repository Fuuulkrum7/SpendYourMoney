import hashlib
from threading import Thread

import tinkoff.invest
from tinkoff.invest import Client, RequestError

from database.database_info import UserTableSQLAlchemy, UserTable
from database.database_interface import DatabaseInterface
from info.user import User


class CheckUser(Thread):
    """
    class for checking user data. codes:
    2** - success
    200 - user exists in db and remotely
    201 - user exists locally, but remotely we did not check
    202 - locally does not exist, remotely - yes
    211 - locally ok, remotely - error
    3**
    300 - error occurred, remotely did not check
    301 - no data locally, remotely - did not check
    4**
    400 - locally - ok, remotely - no user
    5**
    full troubles
    """
    password: str
    login: str
    user: User
    status_code: int = 201

    def __init__(self, login: str, password: str, on_finish, token: str = ""):
        super().__init__()
        self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        self.login = login
        self.__token = token
        self.on_finish = on_finish

    def run(self) -> None:
        try:
            db = DatabaseInterface()
            db.connect_to_db()

            table = UserTableSQLAlchemy()

            result = db.get_data_by_sql(
                {table.get_name(): [UserTable.UID, UserTable.token,
                                    UserTable.username, UserTable.access_level,
                                    UserTable.status]},
                table.get_name(),
                where=f" WHERE {UserTable.username.value} = {self.login} AND "
                      f"{UserTable.password.value} = {self.password} "
            )

            if result:
                self.user = User(**result[0])
            else:
                self.status_code = 301
        except Exception as e:
            print(e)
            self.status_code = 300

        if self.__token:
            with Client(self.__token) as client:
                try:
                    result = client.users.get_accounts().accounts

                    result = list(filter(
                        lambda x: x.status != tinkoff.invest.AccountStatus.
                        ACCOUNT_STATUS_CLOSED and x.access_level != tinkoff.
                        invest.AccessLevel.ACCOUNT_ACCESS_LEVEL_NO_ACCESS,
                        result
                    ))

                    if not len(result):
                        self.status_code = 500 if self.status_code >= 300 \
                            else 400
                    else:
                        self.status_code = 200 if self.status_code == 201 \
                            else 202
                except RequestError as e:
                    print(e)
                    self.status_code = 500 if self.status_code >= 300 \
                        else 211

        self.on_finish(self.status_code)


class CreateUser(Thread):
    user: User
    status_code: int = 200
    password: str

    def __init__(self, user: User, password: str, on_finish):
        super().__init__()

        self.user = user
        self.password = password
        self.on_finish = on_finish

    def run(self) -> None:
        check = CheckUser(
            self.user.username,
            self.password,
            lambda x: x,
            token=self.user.get_token()
        )
        check.start()
        check.join()

        code = check.status_code

        # Все ок, создаем пользователя
        if code == 202:
            try:
                db = DatabaseInterface()
                db.connect_to_db()

                query = self.user.get_as_dict()
                query["password"] = \
                    hashlib.sha512(self.password.encode('utf-8')).hexdigest()

                table = UserTableSQLAlchemy()
                db.add_data(
                    table.get_table(),
                    values=query
                )

                db.close_engine()
            except Exception as e:
                print(e)
                self.status_code = 300
        # пользователь уже есть
        elif code in [200, 211]:
            self.status_code = 100
        # кривой токен/его вообще нет
        elif code in [400, 201, 300, 301]:
            self.status_code = 101
        # Ошибка необрабатываемая
        else:
            self.status_code = 500
