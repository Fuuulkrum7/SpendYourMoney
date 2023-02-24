import hashlib
from threading import Thread

from database.database_info import UserTableSQLAlchemy, UserTable
from database.database_interface import DatabaseInterface
from info.user import User


class CheckUser(Thread):
    password: str
    login: str
    user: User
    status_code = 200

    def __init__(self, login: str, password: str):
        super().__init__()
        self.password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        self.login = login

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
                self.status_code = 400
        except Exception as e:
            print(e)
            self.status_code = 300
