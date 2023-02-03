from database.database_interface import DatabaseValue
from database.database_info import SecuritiesInfo, \
    CouponInfo, DividendInfo, BondsInfo, StocksInfo
from securiries_types import StockType, CouponType
from datetime import datetime, date


class SecurityInfo:
    # Сколько аргументов надо для инициализации
    required_args = 4
    figi: str
    ticker: str
    name: str
    id: int = 0

    def __init__(self, *args):
        """
        :param args: int id, str figi, str ticker, str name
        """
        # Если у нас ничего не передано
        # Обозначаем, что все плохо
        if not len(args):
            self.id = -1
        # Если данных столько, сколько нужно
        elif len(args) == self.required_args:
            self.id = args[0]
            self.figi = args[1]
            self.ticker = args[2]
            self.name = args[3]
        # Если это создание копии существующего класса
        elif isinstance(args[0], SecurityInfo):
            s: SecurityInfo = args[0]
            self.__init__(s.id, s.figi, s.ticker, s.name)
        #
        elif isinstance(args[0], list) and isinstance(args[0][0], DatabaseValue):
            d: list[DatabaseValue] = args[0]
            for value in d:
                if value.get_row_name() == SecuritiesInfo.security_name.name:
                    self.name = str(d[0].get_value())
                elif value.get_row_name() == SecuritiesInfo.figi.name:
                    self.figi = str(d[1].get_value())
                elif value.get_row_name() == SecuritiesInfo.ticker.name:
                    self.ticker = str(d[2].get_value())
                elif value.get_row_name() == SecuritiesInfo.ID.name:
                    self.id = int(str(d[3].get_value()))
                else:
                    self.id = -1
                    return
        else:
            self.id = -1

    def get_as_database_value(self) -> list[DatabaseValue]:
        values: list[DatabaseValue] = [
            DatabaseValue(SecuritiesInfo.ID, self.id),
            DatabaseValue(SecuritiesInfo.figi, self.figi),
            DatabaseValue(SecuritiesInfo.ticker, self.ticker),
            DatabaseValue(SecuritiesInfo.security_name, self.name)
        ]

        return values


class Coupon:
    # Сколько аргументов передано должно быть передано
    __requires = 7
    coupon_id: int
    coupon_date: date
    coupon_number: int
    fix_date: date
    pay_one_bound: float
    coupon_type: CouponType
    security_id: int

    def __init__(
            self,
            coupon_id: int,
            coupon_date: date | str,
            coupon_number: int,
            fix_date: date | str,
            pay_one_bond: float,
            coupon_type: int):
        if isinstance(coupon_date, str):
            self.coupon_date = datetime.strptime(coupon_date, "%Y-%m-%d").date()
        else:
            self.coupon_date = coupon_date
        if isinstance(fix_date, str):
            self.fix_date = datetime.strptime(fix_date, "%Y-%m-%d").date()
        else:
            self.fix_date = fix_date

        self.coupon_id = coupon_id
        self.coupon_number = coupon_number
        self.pay_one_bound = pay_one_bond
        self.coupon_type = CouponType(coupon_type)

    def get_as_database_value(self) -> list[DatabaseValue]:
        values: list[DatabaseValue] = [
            DatabaseValue(CouponInfo.ID, self.coupon_id),
            DatabaseValue(CouponInfo.security_id, self.security_id),
            DatabaseValue(CouponInfo.coupon_date, self.coupon_date),
            DatabaseValue(CouponInfo.coupon_number, self.coupon_number),
            DatabaseValue(CouponInfo.fix_date, self.fix_date),
            DatabaseValue(CouponInfo.pay_one_bond, self.pay_one_bound),
            DatabaseValue(CouponInfo.coupon_type, self.coupon_type.value)
        ]

        return values


class Security:
    __required_args = 5
    class_code: str
    lot: int
    currency: str
    country: str
    sector: str
    info: SecurityInfo

    def __init__(self, *args):
        """
        :param args: class_code, lot, currency, country, sector, other - like for SecurityInfo;
        :type args: str, int, str, str, str, other like in SecurityInfo.
        """
        if not len(args):
            self.info.id = SecurityInfo()
        elif len(args) == self.__required_args + 1:
            self.class_code = args[0]
            self.lot = args[1]
            self.currency = args[2]
            self.country = args[3]
            self.sector = args[4]
            self.info = args[5]
        elif len(args) == self.__required_args + SecurityInfo.required_args:
            self.class_code = args[0]
            self.lot = args[1]
            self.currency = args[2]
            self.country = args[3]
            self.sector = args[4]
            self.info = SecurityInfo(args[5:len(args)])
        elif isinstance(args[0], Security):
            s: Security = args[0]
            self.__init__(s.class_code, s.lot, s.currency, s.country,
                          s.info, s.sector)
        elif isinstance(args[0], list) and isinstance(args[0][0], DatabaseValue):
            d: list[DatabaseValue] = args[0]
            for_info: list[DatabaseValue] = []
            for value in d:
                if value.get_row_name() == SecuritiesInfo.class_code:
                    self.class_code = str(value.get_value())
                elif value.get_row_name() == SecuritiesInfo.class_code:
                    self.lot = int(str(value.get_value()))
                elif value.get_row_name() == SecuritiesInfo.class_code:
                    self.currency = str(value.get_value())
                elif value.get_row_name() == SecuritiesInfo.class_code:
                    self.country = str(value.get_value())
                elif value.get_row_name() == SecuritiesInfo.class_code:
                    self.sector = str(value.get_value())
                elif value.get_row_name() in [i.name for i in SecuritiesInfo]:
                    for_info.append(value)
                else:
                    self.info.id = SecurityInfo()
                    return
            if len(for_info) == 4:
                self.info = SecurityInfo(for_info)
            else:
                self.info.id = SecurityInfo()
        else:
            self.info.id = SecurityInfo()

    def get_as_database_value(self) -> list[DatabaseValue]:
        values: list[DatabaseValue] = [
            DatabaseValue(SecuritiesInfo.class_code, self.class_code),
            DatabaseValue(SecuritiesInfo.lot, self.lot),
            DatabaseValue(SecuritiesInfo.currency, self.currency),
            DatabaseValue(SecuritiesInfo.country, self.country),
            DatabaseValue(SecuritiesInfo.sector, self.sector)
        ]

        values.extend(self.info.get_as_database_value())

        return values


class Bond(Security):
    rate: float
    payments_per_year: int
    nominal: float = 1000
    amortization: bool
    maturity_date: date
    bond_id: int
    aci_value: float
    issue_size: int
    issue_size_plan: int
    floating_coupon: bool
    perpetual: bool
    coupon: Coupon

    def __init__(self, payments_per_year: int, nominal: float, amortization: bool, maturity_date: date | str,
                 bound_id: int, aci_value: float, coupon: Coupon, issue_size: int, issue_plan: int,
                 floating_coupon: bool, perpetual: bool,
                 *args):
        if len(args) == 1:
            super.__init__(args[0])
        else:
            super().__init__(*args)
        self.payments_per_year = payments_per_year
        self.nominal = nominal
        self.rate = round(coupon.pay_one_bound * payments_per_year / nominal * 100, 2)

        if isinstance(maturity_date, str):
            self.maturity_date = datetime.strptime(maturity_date, "%Y-%m-%d").date()
        else:
            self.maturity_date = maturity_date

        self.amortization = amortization
        self.bond_id = bound_id
        self.aci_value = aci_value
        self.issue_size = issue_size
        self.issue_size_plan = issue_plan
        self.floating_coupon = floating_coupon
        self.perpetual = perpetual
        self.coupon = coupon
