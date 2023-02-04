from database.database_interface import DatabaseValue
from database.database_info import SecuritiesInfo, \
    CouponInfo, DividendInfo, BondsInfo, StocksInfo
from securiries_types import StockType, CouponType, SecurityType
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
    coupon_id: int = 0
    coupon_date: date
    coupon_number: int
    fix_date: date
    pay_one_bound: float
    coupon_type: CouponType
    security_id: SecurityType

    def __init__(
            self, *args):
        if len(args) == 1 and isinstance(args[0], list) and isinstance(args[0][0], DatabaseValue):
            d: list[DatabaseValue] = args[0]
            for value in d:
                if value.get_row_name() == CouponInfo.coupon_date:
                    if isinstance(value.get_value(), str):
                        self.coupon_date = datetime.strptime(str(value.get_value()), "%Y-%m-%d").date()
                    else:
                        self.coupon_date = value.get_value()
                elif value.get_row_name() == CouponInfo.fix_date:
                    if isinstance(value.get_value(), str):
                        self.fix_date = datetime.strptime(value.get_value(), "%Y-%m-%d").date()
                    else:
                        self.fix_date = value.get_value()

                elif value.get_row_name() == CouponInfo.ID:
                    self.coupon_id = value.get_value()
                elif value.get_row_name() == CouponInfo.coupon_number:
                    self.coupon_number = value.get_value()
                elif value.get_row_name() == CouponInfo.pay_one_bond:
                    self.pay_one_bound = value.get_value()
                elif value.get_row_name() == CouponInfo.coupon_type:
                    self.coupon_type = CouponType(value.get_value())
                elif value.get_row_name() == CouponInfo.security_id:
                    self.security_id = value.get_value()
                else:
                    self.coupon_id = -1
                    return

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
    __required_args = 6
    class_code: str
    lot: int
    currency: str
    country: str
    sector: str
    info: SecurityInfo
    security_type: SecurityType

    def __init__(self, *args):
        """
        :param args: class_code, lot, currency, country, sector, security_type, SecurityInfo or others
                                                                                        - like for SecurityInfo;
        """
        if not len(args):
            self.info.id = SecurityInfo()
        elif len(args) == self.__required_args + 1:
            self.class_code = args[0]
            self.lot = args[1]
            self.currency = args[2]
            self.country = args[3]
            self.sector = args[4]
            self.security_type = args[5]
            self.info = args[6]
        elif len(args) == self.__required_args + SecurityInfo.required_args:
            self.class_code = args[0]
            self.lot = args[1]
            self.currency = args[2]
            self.country = args[3]
            self.sector = args[4]
            self.security_type = args[5]
            self.info = SecurityInfo(args[6:len(args)])
        elif isinstance(args[0], Security):
            s: Security = args[0]
            self.__init__(s.class_code, s.lot, s.currency, s.country,
                          s.sector, s.security_type, s.info)
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
                elif value.get_row_name() == SecuritiesInfo.security_type:
                    self.security_type = SecurityType(value.get_value())
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
    coupon_quantity_per_year: int
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

    def __init__(self, *args):
        """
        :param args: list[DatabaseValue] for Security or Security, list[DatabaseValue] for Bond,
        list[DatabaseValue] for Coupon
        """
        if len(args) == 3 and ((isinstance(args[0], list) and isinstance(args[0][0], DatabaseValue))
                               or (isinstance(args[0], Security))) \
                and isinstance(args[1], list) and isinstance(args[1][0], DatabaseValue) and \
                isinstance(args[2], list) and isinstance(args[2][0], DatabaseValue):
            super.__init__(args[0])

            d: list[DatabaseValue] = args[1]
            for value in d:
                if value.get_row_name() == BondsInfo.coupon_quantity_per_year:
                    self.coupon_quantity_per_year = value.get_value()
                elif value.get_row_name() == BondsInfo.nominal:
                    self.nominal = value.get_value()
                elif value.get_row_name() == BondsInfo.maturity_date:
                    if isinstance(value.get_value(), str):
                        self.maturity_date = datetime.strptime(value.get_value(), "%Y-%m-%d").date()
                    else:
                        self.maturity_date = value.get_value()
                elif value.get_row_name() == BondsInfo.amortization_flag:
                    self.amortization = value.get_value()
                elif value.get_row_name() == BondsInfo.ID:
                    self.bond_id = value.get_value()
                elif value.get_row_name() == BondsInfo.aci_value:
                    self.aci_value = value.get_value()
                elif value.get_row_name() == BondsInfo.issue_size:
                    self.issue_size = value.get_value()
                elif value.get_row_name() == BondsInfo.issue_size_plan:
                    self.issue_size_plan = value.get_value()
                elif value.get_row_name() == BondsInfo.floating_coupon_flag:
                    self.floating_coupon = value.get_value()
                elif value.get_row_name() == BondsInfo.perpetual_flag:
                    self.perpetual = value.get_value()
                else:
                    self.bond_id = -1
                    try:
                        self.info.id = -1
                    except Exception as e:
                        print(e)
                    return

            self.coupon = Coupon(args[2])
            if self.coupon.coupon_id >= 0:
                self.rate = round(self.coupon.pay_one_bound * self.coupon_quantity_per_year / self.nominal * 100, 2)
            else:
                self.bond_id = -1
                self.info.id = -1
        else:
            super().__init__()
            self.bond_id = -1
