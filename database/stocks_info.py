from enum import Enum


class StocksInfo(Enum):
    ID = "INT"
    security_id = "INT"
    ipo_date = "DATE"
    issue_size = "INT"
    stock_type = "INT"
    otc_flag = "BOOL"
    div_yield_flag = "BOOL"
