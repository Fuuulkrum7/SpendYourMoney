from enum import Enum


class SecuritiesInfo(Enum):
    ID = "INT"
    figi = "CHAR"
    ticker = "CHAR"
    name = "CHAR"
    class_code = "CHAR"
    lot = "INT"
    currency = "CHAR"
    country = "CHAR"
    sector = "CHAR"
