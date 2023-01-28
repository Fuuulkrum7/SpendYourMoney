from enum import Enum


class DividendInfo(Enum):
    ID = "INT"
    security_id = "INT"
    div_value = "DOUBLE"
    payment_date = "DATE"
    declared_date = "DATE"
    record_date = "DATE"
    last_buy_date = "DATE"
    yield_value = "DOUBLE"
