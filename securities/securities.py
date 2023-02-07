from database.database_interface import DatabaseValue
from database.database_info import SecuritiesInfo, \
    CouponInfo, DividendInfo, BondsInfo, StocksInfo
from securities.securiries_types import StockType, CouponType, SecurityType
from datetime import datetime, date

from tinkoff.invest import Dividend as tinkoffDiv, MoneyValue
from tinkoff.invest import Coupon as tinkoffCoupon
from tinkoff.invest.utils import quotation_to_decimal
from math import log10, ceil


# Парсит данные из значения в дату
def get_data_from_value(value: DatabaseValue) -> date:
    if isinstance(value.get_value(), str):
        return datetime.strptime(str(value.get_value()), "%Y-%m-%d").date()
    return value.get_value()


def convert_money_value(data: MoneyValue):
    return data.units + data.nano / 10 ** ceil(log10(data.nano))

class SecurityInfo:
    """
    Общая информация о цб. Содержит id, название, фиги и тикер
    """
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
        # Если получили список DatabaseValue, т.е. только что спарсили из бд
        elif isinstance(args[0], list) and isinstance(args[0][0], DatabaseValue):
            d: list[DatabaseValue] = args[0]
            # перебор списка, чтобы
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
    security_id: int

    def __init__(
            self, *args):
        if len(args) == 1 and isinstance(args[0], list) and isinstance(args[0][0], DatabaseValue):
            d: list[DatabaseValue] = args[0]
            for value in d:
                if value.get_row_name() == CouponInfo.coupon_date:
                    self.coupon_date = get_data_from_value(value)
                elif value.get_row_name() == CouponInfo.fix_date:
                    self.fix_date = get_data_from_value(value)
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
        elif len(args) == 3 and isinstance(args[0], tinkoffCoupon):
            coupon: tinkoffCoupon = args[0]
            self.coupon_date = coupon.coupon_date.date()
            self.fix_date = coupon.fix_date.date()
            self.coupon_number = coupon.coupon_number
            self.pay_one_bound = convert_money_value(coupon.pay_one_bond)
            self.coupon_type = CouponType(coupon.coupon_type)
            self.coupon_id = args[1]
            self.security_id = args[2]
        else:
            self.coupon_id = -1

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


class Dividend:
    __required_args = 8
    div_value: float
    payment_date: date
    declared_date: date
    record_date: date
    last_buy_date: date
    # Величина доходности
    yield_value: float
    security_id: int
    div_id: int

    def __init__(self, *args):
        """
        :param args: can work only with DatabaseValue!
        """
        if isinstance(args[0], list) and len(args) == 1 \
                and isinstance(args[0][0], DatabaseValue) and len(args[0]) == self.__required_args:
            d: list[DatabaseValue] = args[0]
            for value in d:
                if value.get_row_name() == DividendInfo.payment_date:
                    self.payment_date = get_data_from_value(value)
                elif value.get_row_name() == DividendInfo.declared_date:
                    self.declared_date = get_data_from_value(value)
                if value.get_row_name() == DividendInfo.record_date:
                    self.record_date = get_data_from_value(value)
                elif value.get_row_name() == DividendInfo.last_buy_date:
                    self.last_buy_date = get_data_from_value(value)
                elif value.get_row_name() == DividendInfo.ID:
                    self.div_id = value.get_value()
                elif value.get_row_name() == DividendInfo.div_value:
                    self.div_value = value.get_value()
                elif value.get_row_name() == DividendInfo.yield_value:
                    self.yield_value = value.get_value()
                elif value.get_row_name() == CouponInfo.security_id:
                    self.security_id = value.get_value()
                else:
                    self.div_id = -1
                    return
        elif isinstance(args[0], tinkoffDiv) and len(args) == 3:
            div: tinkoffDiv = args[0]
            self.payment_date = div.payment_date
            self.declared_date = div.declared_date.date()
            self.record_date = div.record_date.date()
            self.last_buy_date = div.last_buy_date.date()
            self.div_value = convert_money_value(div.dividend_net)
            self.yield_value = float(quotation_to_decimal(div.yield_value))
            self.div_id = args[1]
            self.security_id = args[2]
        else:
            self.div_id = -1


class Security:
    __required_args = 6
    class_code: str
    lot: int
    currency: str
    country: str
    sector: str
    security_type: SecurityType
    info: SecurityInfo

    def __init__(self, *args):
        """
        :param args: class_code, lot, currency, country, sector, security_type, SecurityInfo or others
                                                                                        - like for SecurityInfo;
        """
        if not len(args):
            self.info = SecurityInfo()
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
            DatabaseValue(SecuritiesInfo.sector, self.sector),
            DatabaseValue(SecuritiesInfo.security_type, self.security_type.value)
        ]

        values.extend(self.info.get_as_database_value())

        return values


class Bond(Security):
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
    coupon: list[Coupon]

    def __init__(self, *args):
        """
        :param args: list[DatabaseValue] for Security or Security, list[DatabaseValue] for Bond,
        list[DatabaseValue] or Coupon for Coupon
        """
        if len(args) == 3 and ((isinstance(args[0], list) and isinstance(args[0][0], DatabaseValue))
                               or (isinstance(args[0], Security))) and isinstance(args[1], list) and \
                (isinstance(args[2], list) and ((isinstance(args[2][0], list) and
                                                 (isinstance(args[2][0][0], DatabaseValue) or
                                                isinstance(args[2][0][0], tinkoffCoupon))) or
                                                isinstance(args[2][0], Coupon)) or
                    args[2][0] is None):
            super().__init__(args[0])

            if isinstance(args[1][0], DatabaseValue):
                d: list[DatabaseValue] = args[1]
                for value in d:
                    if value.get_row_name() == BondsInfo.coupon_quantity_per_year:
                        self.coupon_quantity_per_year = value.get_value()
                    elif value.get_row_name() == BondsInfo.nominal:
                        self.nominal = value.get_value()
                    elif value.get_row_name() == BondsInfo.maturity_date:
                        self.maturity_date = get_data_from_value(value)
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
            else:
                self.coupon_quantity_per_year = args[1][0]
                self.nominal = args[1][1]
                self.amortization = args[1][2]
                self.maturity_date = args[1][3]
                self.bond_id = args[1][4]
                self.aci_value = args[1][5]
                self.issue_size = args[1][6]
                self.issue_size_plan = args[1][7]
                self.floating_coupon = args[1][8]
                self.perpetual = args[1][9]

            if args[2][0] is not None:
                if isinstance(args[2][0], list) and isinstance(args[2][0][0], DatabaseValue):
                    self.coupon = [Coupon(i) for i in args[2]]
                elif isinstance(args[2][0][0], tinkoffCoupon):
                    self.coupon = [Coupon(i, args[2][1], args[2][2]) for i in args[2][0]]
                else:
                    self.coupon = args[2]
        else:
            super().__init__()
            self.bond_id = -1

    def get_as_database_value(self) -> list[DatabaseValue]:
        values = [
            DatabaseValue(BondsInfo.ID, self.bond_id),
            DatabaseValue(BondsInfo.coupon_quantity_per_year, self.coupon_quantity_per_year),
            DatabaseValue(BondsInfo.aci_value, self.aci_value),
            DatabaseValue(BondsInfo.nominal, self.nominal),
            DatabaseValue(BondsInfo.security_id, self.info.id),
            DatabaseValue(BondsInfo.maturity_date, self.maturity_date),
            DatabaseValue(BondsInfo.amortization_flag, self.amortization),
            DatabaseValue(BondsInfo.issue_size, self.issue_size),
            DatabaseValue(BondsInfo.issue_size_plan, self.issue_size_plan),
            DatabaseValue(BondsInfo.floating_coupon_flag, self.floating_coupon),
            DatabaseValue(BondsInfo.perpetual_flag, self.perpetual)
        ]

        return values

    def get_as_database_value_security(self):
        return super().get_as_database_value()

    def count_rate(self) -> float:
        return round(self.coupon[0].pay_one_bound * self.coupon_quantity_per_year / self.nominal * 100, 2)


class Stock(Security):
    stock_id: int
    ipo_date: date
    issue_size: int
    stock_type: StockType
    otc_flag: bool
    div_yield_flag: bool
    dividend: list[Dividend] | None = None

    def __init__(self, *args):
        """
        :param args: requires data for Security, 7 args for stock, dividend or list of args for coupon
        """
        if len(args) == 3:
            # Если первый аргумент список данных для Security или же сам экземпляр класса,
            # второй - список данных для акции,
            # а третий - None, уже готовый дивидент или же набор аргументов для его создания, то
            # начинаем все расставлять по полочкам
            if ((isinstance(args[0], list) and isinstance(args[0][0], DatabaseValue)) or isinstance(args[0], Security))\
                    and isinstance(args[1], list) and \
                    (args[2][0] is None or isinstance(args[2][0], list)):
                super().__init__(args[0])
                print(args)
                if args[2] is not None:
                    if isinstance(args[2][0], Dividend):
                        self.dividend = args[2]
                    elif isinstance(args[2][0], list) and isinstance(args[2][0][0], DatabaseValue):
                        self.dividend = [Dividend(i) for i in args[2]]
                    elif isinstance(args[2][0][0], tinkoffDiv):
                        self.coupon = [Dividend(i, args[2][1], args[2][2]) for i in args[2][0]]
                    else:
                        self.stock_id = -1
                        self.info = SecurityInfo()
                        return

                if isinstance(args[1][0], DatabaseValue):
                    d: list[DatabaseValue] = args[1]

                    for value in d:
                        if value.get_row_name() == StocksInfo.ID:
                            self.stock_id = value.get_value()
                        elif value.get_row_name() == StocksInfo.stock_type:
                            self.stock_type = StockType(value.get_value())
                        elif value.get_row_name() == StocksInfo.issue_size:
                            self.issue_size = value.get_value()
                        elif value.get_row_name() == StocksInfo.otc_flag:
                            self.otc_flag = value.get_value()
                        elif value.get_row_name() == StocksInfo.div_yield_flag:
                            self.div_yield_flag = value.get_value()
                        elif value.get_row_name() == StocksInfo.ipo_date:
                            self.ipo_date = get_data_from_value(value)
                        else:
                            self.stock_id = -1
                            self.info = SecurityInfo()
                            return
                else:
                    self.stock_id = args[1][0]
                    self.ipo_date = args[1][1]
                    self.issue_size = args[1][2]
                    self.stock_type = args[1][3]
                    self.otc_flag = args[1][4]
                    self.div_yield_flag = args[1][5]
        else:
            self.stock_id = -1
            self.info = SecurityInfo()

    def get_as_database_value(self) -> list[DatabaseValue]:
        values = [
            DatabaseValue(StocksInfo.ID, self.stock_id),
            DatabaseValue(StocksInfo.stock_type, self.stock_type.value),
            DatabaseValue(StocksInfo.issue_size, self.issue_size),
            DatabaseValue(StocksInfo.otc_flag, self.otc_flag),
            DatabaseValue(StocksInfo.div_yield_flag, self.div_yield_flag),
            DatabaseValue(StocksInfo.ipo_date, self.ipo_date)
        ]

        return values

    def get_as_database_value_security(self):
        return super().get_as_database_value()
