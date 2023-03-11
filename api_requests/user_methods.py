import hashlib
from threading import Thread

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
    200 - user exists in db and remotely
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
    password: str
    login: str
    user: User = None
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
                                    UserTable.status, UserTable.password]},
                table.get_name(),
                where=f" WHERE {UserTable.username.value} = '{self.login}' "
            )

            if result:
                result = list(filter(
                    lambda x: x[UserTable.password.value] == self.password,
                    result
                ))

                if len(result):
                    result = result[0]
                    result.pop("password")

                    self.user = User(**result)
                    self.__token = self.user.get_token()
                else:
                    self.status_code = 100
            else:
                self.status_code = 250
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
                        result = result[0]
                        self.status_code = 200 if self.status_code == 201 \
                            else 202
                        self.user = User(
                            token=self.__token,
                            username=self.login,
                            access_level=result.access_level,
                            status=result.status,
                            user_id=0
                        )
                except RequestError as e:
                    print(e)
                    self.status_code = 500 if self.status_code >= 250 \
                        else 211

        Thread(target=self.on_finish, args=(self.status_code, self.user)).\
            start()

    def get_user(self):
        return self.user


class CreateUser(Thread):
    """
    status-codes
    1** - some userdata exists
    100 - user exists
    101 - login exists, password is incorrect
    102 - invalid token.
    """
    user: User = None
    status_code: int = 200
    password: str

    def __init__(self, user: User, password: str, on_finish):
        super().__init__()

        self.user = user
        self.password = password
        self.on_finish = on_finish

    def run(self) -> None:
        check: CheckUser = CheckUser(
            self.user.username,
            self.password,
            lambda x, y: x,
            token=self.user.get_token()
        )
        check.start()
        check.join()

        code = check.status_code

        # Все ок, создаем пользователя
        if code == 202:
            try:
                self.user = check.get_user()

                db = DatabaseInterface()
                db.connect_to_db()

                query = self.user.get_as_dict()
                query["password"] = \
                    hashlib.sha512(self.password.encode('utf-8')).hexdigest()

                table = UserTableSQLAlchemy()
                db.add_data(
                    table=table.get_table(),
                    values=query
                )

                cursor: sqlalchemy.engine.cursor = \
                    db.execute_sql("SELECT MAX(UID) FROM " + table.get_name())

                # Собственно, тут мы их и получаем.
                # И обновляем индекс security_id
                # Чтобы потом можно было найти цб в таблице
                for val in cursor:
                    self.user.set_uid(val[0])
                    break
                db.close_engine()
            except Exception as e:
                print(e)
                self.status_code = 300
        # пользователь уже есть
        elif code in [200, 211]:
            self.status_code = 100
        # Такой логин уже есть
        elif code == 100:
            self.status_code = 101
        # кривой токен/его вообще нет
        elif code in [400, 201, 300, 301]:
            self.status_code = 102
        # Ошибка необрабатываемая
        else:
            self.status_code = 500

        Thread(target=self.on_finish, args=(self.status_code, self.user))\
            .start()

    def get_user(self):
        return self.user
