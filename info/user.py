from database.database_info import UserTable
from info.account_status import AccountStatus
from info.access_level import AccessLevel


class User:
    username: str
    __token: str
    __user_id: int
    status: AccountStatus
    access_level: AccessLevel

    def __init__(
            self,
            token: str = "",
            username: str = "",
            UID: int = 0,
            user_id: int = 0,
            status: AccountStatus or int =
            AccountStatus.ACCOUNT_STATUS_UNSPECIFIED,
            access_level: AccessLevel or int =
            AccessLevel.ACCOUNT_ACCESS_LEVEL_UNSPECIFIED,

    ):
        self.__user_id = max(UID, user_id)
        self.__token = token
        self.username = username
        self.status = status if isinstance(status, AccountStatus) \
            else AccountStatus(status)
        self.access_level = access_level if isinstance(access_level,
                                                       AccessLevel) \
            else AccessLevel(access_level)

    def get_token(self):
        return self.__token

    def get_uid(self):
        return self.__user_id

    def get_as_dict(self) -> dict:
        return {
            UserTable.status: self.status.value,
            UserTable.access_level: self.access_level.value,
            UserTable.username: self.username,
            UserTable.token: self.__token,
            UserTable.UID: self.__user_id
        }
