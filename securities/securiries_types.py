from enum import Enum


class StockType(Enum):
    """
    Класс используется для определения типа акции -
    привилегированная, обычная и тд
    """
    STOCK_TYPE_UNSPECIFIED = 0
    STOCK_TYPE_COMMON = 1
    STOCK_TYPE_PREFERRED = 2
    STOCK_TYPE_ADR = 3
    STOCK_TYPE_GDR = 4
    STOCK_TYPE_MLP = 5
    STOCK_TYPE_NY_REG_SHRS = 6
    STOCK_TYPE_CLOSED_END_FUND = 7
    STOCK_TYPE_REIT = 8


class CouponType(Enum):
    """
    Класс используется для обозначения типов купонов, все аналогично
    Так же для этих двух классов существует json,
    представляющий коды в текстовом формате
    """
    COUPON_TYPE_UNSPECIFIED = 0
    COUPON_TYPE_CONSTANT = 1
    COUPON_TYPE_FLOATING = 2
    COUPON_TYPE_DISCOUNT = 3
    COUPON_TYPE_MORTGAGE = 4
    COUPON_TYPE_FIX = 5
    COUPON_TYPE_VARIABLE = 6
    COUPON_TYPE_OTHER = 7

    def __str__(self):
        return self.name.replace("_", " ").capitalize()


class SecurityType(Enum):
    """
    Тип цб. Больше и не скажешь
    """
    STOCK = 0
    BOND = 1
    DEFAULT = 2
