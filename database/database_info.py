from enum import Enum


class BondsInfo(Enum):
    ID = "INT NOT NULL AUTO_INCREMENT"
    security_id = "INT"
    coupon_quantity_per_year = "INT"
    maturity_date = "DATE"
    nominal = "DOUBLE"
    aci_value = "FLOAT"
    issue_size = "INT"
    issue_size_plan = "INT"
    floating_coupon_flag = "BOOL"
    perpetual_flag = "BOOL"
    amortization_flag = "BOOL"


class CouponInfo(Enum):
    ID = "INT NOT NULL AUTO_INCREMENT"
    security_id = "INT"
    coupon_date = "DATE"
    coupon_number = "INT"
    fix_date = "DATE"
    pay_one_bond = "DOUBLE"
    coupon_type = "INT"


class DividendInfo(Enum):
    ID = "INT NOT NULL AUTO_INCREMENT"
    security_id = "INT"
    div_value = "DOUBLE"
    payment_date = "DATE"
    declared_date = "DATE"
    record_date = "DATE"
    last_buy_date = "DATE"
    yield_value = "DOUBLE"


class SecuritiesHistory(Enum):
    security_id = "INT NOT NULL AUTO_INCREMENT"
    price = "DOUBLE"
    time = "DATETIME"
    volume = "INT"


class SecuritiesInfo(Enum):
    ID = "INT NOT NULL AUTO_INCREMENT"
    figi = "CHAR"
    ticker = "CHAR"
    security_name = "CHAR"
    class_code = "CHAR"
    lot = "INT"
    currency = "CHAR"
    country = "CHAR"
    sector = "CHAR"


class StocksInfo(Enum):
    ID = "INT NOT NULL AUTO_INCREMENT"
    security_id = "INT"
    ipo_date = "DATE"
    issue_size = "INT"
    stock_type = "INT"
    otc_flag = "BOOL"
    div_yield_flag = "BOOL"


class UserTable(Enum):
    UID = "INT NOT NULL AUTO_INCREMENT"
    username = "CHAR"
    token = "CHAR"
    password = "CHAR"
    status = "INT"
    access_level = "INT"

