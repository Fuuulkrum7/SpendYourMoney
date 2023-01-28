from enum import Enum


class BondsInfo(Enum):
    ID = "INT"
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
