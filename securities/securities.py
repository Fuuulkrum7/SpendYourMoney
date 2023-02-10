from database.database_info import SecuritiesInfo, \
    CouponInfo, DividendInfo, BondsInfo, StocksInfo
from securities.securiries_types import StockType, CouponType, SecurityType
from datetime import datetime, date

from tinkoff.invest import MoneyValue, Quotation
from math import log10, ceil


# Парсит данные из значения в дату
def get_data_from_value(value: str | date) -> date:
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    return value


def convert_money_value(data: MoneyValue | Quotation | float):
    if isinstance(data, float):
        return data
    return data.units + data.nano / 10 ** ceil(log10(data.nano if data.nano > 0 else 1))


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
                 ticker: str = None, security_name: str = None, class_code: str = None):
        """
        :param args: int id, str figi, str ticker, str name
        """
        self.id = max(id, ID)
        self.class_code = class_code
        self.figi = figi
        self.ticker = ticker
        self.name = security_name

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = {
            SecuritiesInfo.ID.name: self.id,
            SecuritiesInfo.figi.name: self.figi,
            SecuritiesInfo.ticker.name: self.ticker,
            SecuritiesInfo.security_name.name: self.name,
            SecuritiesInfo.class_code.name: self.class_code
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
            coupon_date: date | str = None,
            coupon_number: int = None,
            fix_date: date | str = None,
            pay_one_bound: float | MoneyValue = None,
            coupon_type: CouponType = None,
            security_id: int = -1):

        self.coupon_id = max(ID, coupon_id)
        self.coupon_date = get_data_from_value(coupon_date)
        self.coupon_number = coupon_number
        self.fix_date = get_data_from_value(fix_date)
        self.pay_one_bound = convert_money_value(pay_one_bound)
        self.coupon_type = coupon_type if isinstance(coupon_type, CouponType) else CouponType(coupon_type)
        self.security_id = security_id

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = {
            CouponInfo.ID.name: self.coupon_id,
            CouponInfo.security_id.name: self.security_id,
            CouponInfo.coupon_date.name: self.coupon_date,
            CouponInfo.coupon_number.name: self.coupon_number,
            CouponInfo.fix_date.name: self.fix_date,
            CouponInfo.pay_one_bond.name: self.pay_one_bound,
            CouponInfo.coupon_type.name: self.coupon_type.value
        }

        return values


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
            div_value: float | MoneyValue = None,
            payment_date: date | str = None,
            declared_date: date | str = None,
            record_date: date | str = None,
            last_buy_date: date | str = None,
            yield_value: float = None,
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
            DividendInfo.ID.name: self.div_id,
            DividendInfo.security_id.name: self.security_id,
            DividendInfo.payment_date.name: self.payment_date,
            DividendInfo.declared_date.name: self.declared_date,
            DividendInfo.record_date.name: self.record_date,
            DividendInfo.last_buy_date.name: self.last_buy_date,
            DividendInfo.div_value.name: self.div_value,
            DividendInfo.yield_value.name: self.yield_value
        }

        return values


class Security:
    __required_args = 6
    lot: int
    currency: str
    country: str
    sector: str
    security_type: SecurityType
    info: SecurityInfo

    def __init__(
            self,
            lot: int = 0,
            currency: str = None,
            country: str = None,
            sector: str = None,
            security_type: SecurityType = SecurityType.DEFAULT,
            info: SecurityInfo = None,
            id: int = -1,
            ID: int = -1,
            class_code: str = None,
            figi: str = None,
            ticker: str = None,
            security_name: str = None
        ):
        """
        :param: class_code, lot, currency, country, sector, security_type, SecurityInfo or others
                                                                                        - like for SecurityInfo;
        """
        self.lot = lot
        self.currency = currency
        self.country = country
        self.sector = sector
        self.security_type = security_type if isinstance(security_type, SecurityType) \
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
        values: dict[str, object] = {
            SecuritiesInfo.lot.name: self.lot,
            SecuritiesInfo.currency.name: self.currency,
            SecuritiesInfo.country.name: self.country,
            SecuritiesInfo.sector.name: self.sector,
            SecuritiesInfo.security_type.name: self.security_type.value
        }

        values.update(self.info.get_as_dict())

        return values

    def set_id(self, id: int):
        self.info.id = id

    def set_security_id(self, id: int):
        self.set_id(id)

    def get_as_dict_security(self):
        return self.get_as_dict()


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
            nominal: float | MoneyValue = 1000,
            amortization: bool = False,
            maturity_date: date | str= None,
            bond_id: int = -1,
            ID: int = -1,
            aci_value: float | MoneyValue = 0,
            issue_size: int = 0,
            issue_size_plan: int = 0,
            floating_coupon: bool = False,
            perpetual: bool = False,
            coupon: list[Coupon] = [],

            security: Security = None,
            lot: int = 0,
            currency: str = None,
            country: str = None,
            sector: str = None,
            security_type: SecurityType = SecurityType.BOND,
            info: SecurityInfo = None,
            id: int = -1,
            class_code: str = None,
            figi: str = None,
            ticker: str = None,
            name: str = None
    ):

        if security is not None:
            super().__init__(**security.get_as_dict())
        else:
            super().__init__(
                lot=lot,
                currency=currency,
                country=country,
                sector=sector,
                security_type=security_type,
                info=info,
                id=id,
                ID=id,
                class_code=class_code,
                figi=figi,
                ticker=ticker,
                security_name=name
            )

        self.coupon = coupon
        self.coupon_quantity_per_year = coupon_quantity_per_year
        self.nominal = convert_money_value(nominal)
        self.amortization = amortization
        self.maturity_date = get_data_from_value(maturity_date)
        self.bond_id = max(bond_id, ID)
        self.aci_value = convert_money_value(aci_value)
        self.issue_size = issue_size
        self.issue_size_plan = issue_size_plan
        self.floating_coupon = floating_coupon
        self.perpetual = perpetual

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = {
            BondsInfo.ID.name: self.bond_id,
            BondsInfo.coupon_quantity_per_year.name: self.coupon_quantity_per_year,
            BondsInfo.aci_value.name: self.aci_value,
            BondsInfo.nominal.name: self.nominal,
            BondsInfo.security_id.name: self.info.id,
            BondsInfo.maturity_date.name: self.maturity_date,
            BondsInfo.amortization_flag.name: self.amortization,
            BondsInfo.issue_size.name: self.issue_size,
            BondsInfo.issue_size_plan.name: self.issue_size_plan,
            BondsInfo.floating_coupon_flag.name: self.floating_coupon,
            BondsInfo.perpetual_flag.name: self.perpetual
        }

        return values

    def get_as_dict_security(self):
        return super().get_as_dict()

    def count_rate(self) -> float:
        return round(self.coupon[0].pay_one_bound * self.coupon_quantity_per_year / self.nominal * 100, 2)

    def set_id(self, id: int):
        self.bond_id = id

    def set_security_id(self, id: int):
        super().set_id(id)
        for i in self.coupon:
            i.security_id = id


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
            sector: str = None,
            security_type: SecurityType = SecurityType.STOCK,
            info: SecurityInfo = None,
            id: int = -1,
            class_code: str = None,
            figi: str = None,
            ticker: str = None,
            name: str = None
    ):
        if security is not None:
            super().__init__(**security.get_as_dict())
        else:
            super().__init__(
                lot=lot,
                currency=currency,
                country=country,
                sector=sector,
                security_type=security_type,
                info=info,
                id=id,
                class_code=class_code,
                figi=figi,
                ticker=ticker,
                name=name
            )

        self.dividend = dividend
        self.stock_id = max(ID, stock_id)
        self.ipo_date = get_data_from_value(ipo_date)
        self.issue_size = issue_size
        self.stock_type = stock_type if isinstance(stock_type, StockType) else StockType(stock_type)
        self.otc_flag = otc_flag
        self.div_yield_flag = div_yield_flag

    def get_as_dict(self) -> dict[str, object]:
        values: dict[str, object] = {
            StocksInfo.ID.name: self.stock_id,
            StocksInfo.stock_type.name: self.stock_type.value,
            StocksInfo.issue_size.name: self.issue_size,
            StocksInfo.otc_flag.name: self.otc_flag,
            StocksInfo.div_yield_flag.name: self.div_yield_flag,
            StocksInfo.ipo_date.name: self.ipo_date,
            StocksInfo.security_id.name: self.info.id
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
