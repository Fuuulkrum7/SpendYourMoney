from enum import Enum


class CouponInfo(Enum):
    ID = "INT"
    security_id = "INT"
    coupon_date = "DATE"
    coupon_number = "INT"
    fix_date = "DATE"
    pay_one_bond = "DOUBLE"
    coupon_type = "INT"
