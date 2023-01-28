from enum import Enum


class SecuritiesHistory(Enum):
    security_id = "INT"
    price = "DOUBLE"
    time = "DATETIME"
    volume = "INT"
