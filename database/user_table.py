from enum import Enum


class UserTable(Enum):
    UID = "INT"
    username = "CHAR"
    token = "CHAR"
    password = "CHAR"
    status = "INT"
    access_level = "INT"
