from info.account_status import AccountStatus
from info.access_level import AccessLevel


class User:
    username: str
    __token: str
    __user_id: int
    status: AccountStatus
    access_level: AccessLevel

    def get_token(self):
        return self.__token

    def get_uid(self):
        return self.__user_id
