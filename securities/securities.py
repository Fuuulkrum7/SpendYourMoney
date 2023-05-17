from database.database_info import SecuritiesInfo, \
    CouponInfo, DividendInfo, BondsInfo, StocksInfo
from securities.securiries_types import StockType, CouponType, SecurityType
from datetime import datetime, date

from tinkoff.invest import MoneyValue, Quotation
from math import log10, ceil


# Парсит данные из значения в дату
def get_data_from_value(value: str or date) -> date:
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    return value


def convert_money_value(data: MoneyValue or Quotation or float):
    if isinstance(data, float):
        return data
    return round(data.units + data.nano / 10 ** ceil(
        log10(data.nano if data.nano > 0 else 1)
    ), 4)


class SecurityInfo:
    """
    Общая информация о цб. Содержит id, название, фиги и тикер
    """
    # Сколько аргументов надо для инициализации
    required_args = 5
    figi: str
    ticker: str
    name: str
    class_code: str
    id: int = 0

    def __init__(self, id: int = -1, figi: str = None, ID: int = -1,
                 ticker: str = None, security_name: str = None,
                 class_code: str = None):
        """
        :param: int id, str FIGI, str ticker, str name, str class_code
        """
        self.id = max(id, ID)
        self.class_code = class_code
        self.figi = figi
        self.ticker = ticker
        self.name = security_name

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = {
            SecuritiesInfo.ID.value: self.id,
            SecuritiesInfo.FIGI.value: self.figi,
            SecuritiesInfo.TICKER.value: self.ticker,
            SecuritiesInfo.SECURITY_NAME.value: self.name,
            SecuritiesInfo.CLASS_CODE.value: self.class_code
        }

        return values


class Coupon:
    coupon_id: int = 0
    coupon_date: date
    coupon_number: int
    fix_date: date
    pay_one_bound: float
    coupon_type: CouponType
    security_id: int

    def __init__(
            self,
            coupon_id: int = -1,
            ID: int = -1,
            coupon_date: date or str = None,
            coupon_number: int = None,
            fix_date: date or str = None,
            pay_one_bond: float or MoneyValue = None,
            coupon_type: CouponType = None,
            security_id: int = -1):

        self.coupon_id = max(ID, coupon_id)
        self.coupon_date = get_data_from_value(coupon_date)
        self.coupon_number = coupon_number
        self.fix_date = get_data_from_value(fix_date)
        self.pay_one_bound = convert_money_value(pay_one_bond)
        self.coupon_type = coupon_type if isinstance(coupon_type, CouponType) \
            else CouponType(coupon_type)
        self.security_id = security_id

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = {
            CouponInfo.ID.value: self.coupon_id,
            CouponInfo.security_id.value: self.security_id,
            CouponInfo.coupon_date.value: self.coupon_date,
            CouponInfo.coupon_number.value: self.coupon_number,
            CouponInfo.fix_date.value: self.fix_date,
            CouponInfo.pay_one_bond.value: self.pay_one_bound,
            CouponInfo.coupon_type.value: self.coupon_type.value
        }

        return values

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return other.pay_one_bound == self.pay_one_bound and \
            other.coupon_date == self.coupon_date

    # И работы с множествами
    def __hash__(self):
        return hash(
            (self.pay_one_bound, self.coupon_date)
        )


class Dividend:
    div_value: float
    payment_date: date
    declared_date: date
    record_date: date
    last_buy_date: date
    # Величина доходности
    yield_value: float
    security_id: int
    div_id: int

    def __init__(
            self,
            div_value: float or MoneyValue = None,
            payment_date: date or str = None,
            declared_date: date or str = None,
            record_date: date or str = None,
            last_buy_date: date or str = None,
            yield_value: float or MoneyValue = None,
            security_id: int = None,
            div_id: int = -1,
            ID: int = -1):
        """
        :param:
        """

        self.div_id = max(div_id, ID)
        self.div_value: float = convert_money_value(div_value)
        self.payment_date = get_data_from_value(payment_date)
        self.declared_date = get_data_from_value(declared_date)
        self.record_date = get_data_from_value(record_date)
        self.last_buy_date = get_data_from_value(last_buy_date)
        self.yield_value = convert_money_value(yield_value)
        self.security_id = security_id

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = {
            DividendInfo.ID.value: self.div_id,
            DividendInfo.security_id.value: self.security_id,
            DividendInfo.payment_date.value: self.payment_date,
            DividendInfo.declared_date.value: self.declared_date,
            DividendInfo.record_date.value: self.record_date,
            DividendInfo.last_buy_date.value: self.last_buy_date,
            DividendInfo.div_value.value: self.div_value,
            DividendInfo.yield_value.value: self.yield_value
        }

        return values

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return other.div_value == self.div_value and \
            other.declared_date == self.declared_date and \
            other.yield_value == self.yield_value

    # Для работы с множествами
    def __hash__(self):
        return hash(
            (self.declared_date, self.div_value, self.yield_value)
        )


class Security:
    lot: int
    currency: str
    country: str
    country_code: str
    sector: str
    security_type: SecurityType
    info: SecurityInfo
    priority: int

    def __init__(
            self,
            lot: int = 0,
            currency: str = None,
            country: str = None,
            country_code: str = None,
            sector: str = None,
            security_type: SecurityType = SecurityType.DEFAULT,
            priority: int = 0,
            info: SecurityInfo = None,
            id: int = -1,
            ID: int = -1,
            class_code: str = None,
            figi: str = None,
            ticker: str = None,
            security_name: str = None):
        """
        :param: class_code, lot, currency, country, sector, SECURITY_TYPE,
        SecurityInfo or others - like for SecurityInfo;
        """
        self.lot = lot
        self.currency = currency
        self.country = country
        self.country_code = country_code
        self.sector = sector
        self.priority = priority
        self.security_type = security_type if isinstance(security_type,
                                                         SecurityType) \
            else SecurityType(security_type)
        if info is not None:
            self.info = info
        else:
            self.info = SecurityInfo(
                id=id,
                ID=ID,
                class_code=class_code,
                figi=figi,
                ticker=ticker,
                security_name=security_name
            )

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = self.info.get_as_dict()

        values.update({
            SecuritiesInfo.LOT.value: self.lot,
            SecuritiesInfo.CURRENCY.value: self.currency,
            SecuritiesInfo.COUNTRY.value: self.country,
            SecuritiesInfo.SECTOR.value: self.sector,
            SecuritiesInfo.SECURITY_TYPE.value: self.security_type.value,
            SecuritiesInfo.COUNTRY_CODE.value: self.country_code,
            SecuritiesInfo.PRIORITY.value: self.priority,
        })

        return values

    def set_id(self, id: int):
        self.info.id = id

    def set_security_id(self, id: int):
        self.set_id(id)

    def get_as_dict_security(self):
        return self.get_as_dict()

    def get_sub_data(self) -> list:
        return []


class Bond(Security):
    coupon_quantity_per_year: int
    nominal: float
    amortization: bool
    maturity_date: date
    bond_id: int
    aci_value: float
    issue_size: int
    issue_size_plan: int
    floating_coupon: bool
    perpetual: bool
    coupon: list[Coupon] = []

    def __init__(
            self,
            coupon_quantity_per_year: int = 0,
            nominal: float or MoneyValue = 1000.0,
            amortization_flag: bool = False,
            maturity_date: date or str = None,
            bond_id: int = -1,
            ID: int = -1,
            aci_value: float or MoneyValue = 0.0,
            issue_size: int = 0,
            issue_size_plan: int = 0,
            floating_coupon_flag: bool = False,
            perpetual_flag: bool = False,
            coupon: list[Coupon] = [],

            security: Security = None,
            lot: int = 0,
            currency: str = None,
            country: str = None,
            country_code: str = None,
            priority: int = 0,
            sector: str = None,
            security_type: SecurityType = SecurityType.BOND,
            info: SecurityInfo = None,
            security_id: int = -1,
            class_code: str = None,
            figi: str = None,
            ticker: str = None,
            security_name: str = None
    ):

        if security is not None:
            super().__init__(**security.get_as_dict())
        else:
            super().__init__(
                lot=lot,
                currency=currency,
                country=country,
                country_code=country_code,
                sector=sector,
                security_type=security_type,
                info=info,
                id=security_id,
                class_code=class_code,
                figi=figi,
                ticker=ticker,
                priority=priority,
                security_name=security_name
            )

        self.coupon = coupon
        self.coupon_quantity_per_year = coupon_quantity_per_year
        self.nominal = convert_money_value(nominal)
        self.amortization = amortization_flag
        self.maturity_date = get_data_from_value(maturity_date)
        self.bond_id = max(bond_id, ID)
        self.aci_value = convert_money_value(aci_value)
        self.issue_size = issue_size
        self.issue_size_plan = issue_size_plan
        self.floating_coupon = floating_coupon_flag
        self.perpetual = perpetual_flag

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = {
            BondsInfo.ID.value: self.bond_id,
            BondsInfo.coupon_quantity_per_year.value:
                self.coupon_quantity_per_year,
            BondsInfo.aci_value.value: self.aci_value,
            BondsInfo.nominal.value: self.nominal,
            BondsInfo.security_id.value: self.info.id,
            BondsInfo.maturity_date.value: self.maturity_date,
            BondsInfo.amortization_flag.value: self.amortization,
            BondsInfo.issue_size.value: self.issue_size,
            BondsInfo.issue_size_plan.value: self.issue_size_plan,
            BondsInfo.floating_coupon_flag.value: self.floating_coupon,
            BondsInfo.perpetual_flag.value: self.perpetual
        }

        return values

    def get_as_dict_security(self):
        return super().get_as_dict()

    def count_rate(self) -> float:
        return round(self.coupon[0].pay_one_bound *
                     self.coupon_quantity_per_year / self.nominal * 100, 2)

    def set_id(self, id: int):
        self.bond_id = id

    def set_security_id(self, id: int):
        super().set_id(id)
        for i in self.coupon:
            i.security_id = id

    def get_sub_data(self) -> list:
        return self.coupon


class Stock(Security):
    stock_id: int
    ipo_date: date
    issue_size: int
    stock_type: StockType
    otc_flag: bool
    div_yield_flag: bool
    dividend: list[Dividend]

    def __init__(
            self,
            stock_id: int = -1,
            ID: int = -1,
            ipo_date: date = None,
            issue_size: int = 0,
            stock_type: StockType = None,
            otc_flag: bool = False,
            div_yield_flag: bool = False,
            dividend: list[Dividend] = [],

            security: Security = None,
            lot: int = 0,
            currency: str = None,
            country: str = None,
            country_code: str = None,
            priority: int = 0,
            sector: str = None,
            security_type: SecurityType = SecurityType.STOCK,
            info: SecurityInfo = None,
            security_id: int = -1,
            class_code: str = None,
            figi: str = None,
            ticker: str = None,
            security_name: str = None
    ):
        if security is not None:
            super().__init__(**security.get_as_dict())
        else:
            super().__init__(
                lot=lot,
                currency=currency,
                country=country,
                country_code=country_code,
                sector=sector,
                security_type=security_type,
                priority=priority,
                info=info,
                id=security_id,
                class_code=class_code,
                figi=figi,
                ticker=ticker,
                security_name=security_name
            )

        self.dividend = dividend
        self.stock_id = max(ID, stock_id)
        self.ipo_date = get_data_from_value(ipo_date)
        self.issue_size = issue_size
        self.stock_type = stock_type if isinstance(stock_type, StockType) \
            else StockType(stock_type)
        self.otc_flag = otc_flag
        self.div_yield_flag = div_yield_flag

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = {
            StocksInfo.ID.value: self.stock_id,
            StocksInfo.stock_type.value: self.stock_type.value,
            StocksInfo.issue_size.value: self.issue_size,
            StocksInfo.otc_flag.value: self.otc_flag,
            StocksInfo.div_yield_flag.value: self.div_yield_flag,
            StocksInfo.ipo_date.value: self.ipo_date,
            StocksInfo.security_id.value: self.info.id
        }

        return values

    def get_as_dict_security(self):
        return super().get_as_dict()

    def set_id(self, id: int):
        self.stock_id = id

    def set_security_id(self, id: int):
        super().set_id(id)
        for i in self.dividend:
            i.security_id = id

    def get_sub_data(self) -> list:
        return self.dividend
