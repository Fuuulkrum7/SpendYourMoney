"""
Здесь находятся классы для работы с базой данных.
В частности, тут находятся классы-нумераторы, содержащие всю информацию
о столбцах в бд (используются для запросов к бд) и классы sqlalchemy (Base),
по сути тоже сами по себе таблицы
"""
from enum import Enum

import sqlalchemy
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BondsInfo(Enum):
    """
    Текущий и дальнейшие классы до соответствующего комментария
    имеют одинаковую структуру.
    Все имена переменный соответствуют именам столбцов
    в соответствующих базах данных. А значения переменных - типам данных.
    Удобно для конвертации данных обратно, из бд
    """
    ID = "ID"
    security_id = "security_id"
    coupon_quantity_per_year = "coupon_quantity_per_year"
    maturity_date = "maturity_date"
    nominal = "nominal"
    aci_value = "aci_value"
    issue_size = "issue_size"
    issue_size_plan = "issue_size_plan"
    floating_coupon_flag = "floating_coupon_flag"
    perpetual_flag = "perpetual_flag"
    amortization_flag = "amortization_flag"


class CouponInfo(Enum):
    ID = "ID"
    security_id = "security_id"
    coupon_date = "coupon_date"
    coupon_number = "coupon_number"
    fix_date = "fix_date"
    pay_one_bond = "pay_one_bond"
    coupon_type = "coupon_type"


class DividendInfo(Enum):
    ID = "ID"
    security_id = "security_id"
    div_value = "div_value"
    payment_date = "payment_date"
    declared_date = "declared_date"
    record_date = "record_date"
    last_buy_date = "last_buy_date"
    yield_value = "yield_value"


class SecuritiesHistory(Enum):
    security_id = "security_id"
    price = "price"
    info_time = "info_time"
    volume = "volume"
    CANDLE_INTERVAL = "candle_interval"


class SecuritiesInfo(Enum):
    ID = "ID"
    FIGI = "figi"
    TICKER = "ticker"
    SECURITY_NAME = "security_name"
    CLASS_CODE = "class_code"
    LOT = "lot"
    CURRENCY = "currency"
    COUNTRY = "country"
    SECTOR = "sector"
    SECURITY_TYPE = "security_type"
    COUNTRY_CODE = "country_code"
    PRIORITY = "priority"


class StocksInfo(Enum):
    ID = "ID"
    security_id = "security_id"
    ipo_date = "ipo_date"
    issue_size = "issue_size"
    stock_type = "stock_type"
    otc_flag = "otc_flag"
    div_yield_flag = "div_yield_flag"


class UserTable(Enum):
    UID = "UID"
    username = "username"
    token = "token"
    password = "password"
    status = "status"
    access_level = "access_level"


# Таблицы для SQLAlchemy
class UserTableSQLAlchemy(Base):
    """
    Собственно, тут принцип прост. Это базовый класс, который содержит
    поля таблиц, что нужно для обращения
    к базе данных. В классе DatabaseValue мы храним
    одно из полей вышестоящих классов,
    при добавлении в бд мы получаем с помощью
    цикла данные в формате ключ-значение.
    Это позволяет сделать универсальный метод добавления
    любых данных в любую таблицу из представленных здесь.
    Этот класс и ему подобные нужны для хранения таблицы в том виде,
     в котором они понятны для sqlalchemy.
    Для этого в них есть поле __table__ и соответствующий метод.
    Переменные же нужны для работы с конкретными
    столбцами, что теоретически может пригодиться
    при дальнейшем расширении базы данных.
    """
    __tablename__ = "user_table"

    UID = sqlalchemy.Column("UID", sqlalchemy.Integer, primary_key=True,
                            autoincrement=True)
    username = sqlalchemy.Column("username", sqlalchemy.VARCHAR)
    token = sqlalchemy.Column("token", sqlalchemy.VARCHAR)
    password = sqlalchemy.Column("password", sqlalchemy.VARCHAR)
    status = sqlalchemy.Column("status", sqlalchemy.Integer)
    access_level = sqlalchemy.Column("access_level", sqlalchemy.Integer)

    __table__ = sqlalchemy.Table(
        __tablename__,
        Base.metadata,
        UID,
        username,
        token,
        password,
        status,
        access_level
    )

    def get_table(self):
        return self.__table__

    def get_name(self):
        return self.__tablename__


class SecuritiesInfoTable(Base):
    __tablename__ = "securities_info"
    __table_args__ = {'extend_existing': True}

    ID = sqlalchemy.Column("ID", sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    figi = sqlalchemy.Column("figi", sqlalchemy.VARCHAR)
    ticker = sqlalchemy.Column("ticker", sqlalchemy.VARCHAR)
    security_name = sqlalchemy.Column("security_name", sqlalchemy.VARCHAR)
    class_code = sqlalchemy.Column("class_code", sqlalchemy.VARCHAR)
    lot = sqlalchemy.Column("lot", sqlalchemy.Integer)
    currency = sqlalchemy.Column("currency", sqlalchemy.VARCHAR)
    country = sqlalchemy.Column("country", sqlalchemy.VARCHAR)
    sector = sqlalchemy.Column("sector", sqlalchemy.VARCHAR)
    security_type = sqlalchemy.Column("security_type", sqlalchemy.Integer)
    country_code = sqlalchemy.Column("country_code", sqlalchemy.VARCHAR)
    priority = sqlalchemy.Column("priority", sqlalchemy.Integer)

    __table__ = sqlalchemy.Table(
        __tablename__,
        Base.metadata,
        ID,
        figi,
        ticker,
        security_name,
        class_code,
        lot,
        currency,
        country,
        country_code,
        sector,
        security_type,
        priority
    )

    def get_table(self):
        return self.__table__

    def get_name(self):
        return self.__tablename__


class BondsInfoTable(Base):
    __tablename__ = "bonds_info"
    __table_args__ = {'extend_existing': True}

    ID = sqlalchemy.Column("ID", sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    security_id = sqlalchemy.Column("security_id", sqlalchemy.Integer,
                                    nullable=False)
    coupon_quantity_per_year = sqlalchemy.Column("coupon_quantity_per_year",
                                                 sqlalchemy.Integer)
    maturity_date = sqlalchemy.Column("maturity_date", sqlalchemy.Date)
    nominal = sqlalchemy.Column("nominal", DOUBLE)
    aci_value = sqlalchemy.Column("aci_value", DOUBLE)
    issue_size = sqlalchemy.Column("issue_size", sqlalchemy.Integer)
    issue_size_plan = sqlalchemy.Column("issue_size_plan", sqlalchemy.Integer)
    floating_coupon_flag = sqlalchemy.Column("floating_coupon_flag",
                                             sqlalchemy.Boolean)
    perpetual_flag = sqlalchemy.Column("perpetual_flag", sqlalchemy.Boolean)
    amortization_flag = sqlalchemy.Column("amortization_flag",
                                          sqlalchemy.Boolean)

    __table__ = sqlalchemy.Table(
        __tablename__,
        Base.metadata,
        ID,
        security_id,
        coupon_quantity_per_year,
        maturity_date,
        nominal,
        aci_value,
        issue_size,
        issue_size_plan,
        floating_coupon_flag,
        perpetual_flag,
        amortization_flag
    )

    def get_table(self):
        return self.__table__

    def get_name(self):
        return self.__tablename__


class CouponInfoTable(Base):
    __tablename__ = "coupon_info"

    ID = sqlalchemy.Column("ID", sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    security_id = sqlalchemy.Column("security_id", sqlalchemy.Integer,
                                    nullable=False)
    coupon_date = sqlalchemy.Column("coupon_date", sqlalchemy.Date)
    coupon_number = sqlalchemy.Column("coupon_number", sqlalchemy.Integer)
    fix_date = sqlalchemy.Column("fix_date", sqlalchemy.Date)
    pay_one_bond = sqlalchemy.Column("pay_one_bond", DOUBLE)
    coupon_type = sqlalchemy.Column("coupon_type", sqlalchemy.Integer)

    __table__ = sqlalchemy.Table(
        __tablename__,
        Base.metadata,
        ID,
        security_id,
        coupon_date,
        coupon_number,
        fix_date,
        pay_one_bond,
        coupon_type
    )

    def get_table(self):
        return self.__table__

    def get_name(self):
        return self.__tablename__


class StocksInfoTable(Base):
    __tablename__ = "stocks_info"
    __table_args__ = {'extend_existing': True}

    ID = sqlalchemy.Column("ID", sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    security_id = sqlalchemy.Column("security_id", sqlalchemy.Integer,
                                    nullable=False)
    ipo_date = sqlalchemy.Column("ipo_date", sqlalchemy.Date)
    issue_size = sqlalchemy.Column("issue_size", sqlalchemy.Integer)
    stock_type = sqlalchemy.Column("stock_type", sqlalchemy.Integer)
    otc_flag = sqlalchemy.Column("otc_flag", sqlalchemy.Boolean)
    div_yield_flag = sqlalchemy.Column("div_yield_flag", sqlalchemy.Boolean)

    __table__ = sqlalchemy.Table(
        __tablename__,
        Base.metadata,
        ID,
        security_id,
        ipo_date,
        issue_size,
        stock_type,
        otc_flag,
        div_yield_flag
    )

    def get_table(self):
        return self.__table__

    def get_name(self):
        return self.__tablename__


class DividendInfoTable(Base):
    __tablename__ = "dividend_info"

    ID = sqlalchemy.Column("ID", sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    security_id = sqlalchemy.Column("security_id", sqlalchemy.Integer,
                                    nullable=False)
    div_value = sqlalchemy.Column("div_value", DOUBLE)
    payment_date = sqlalchemy.Column("payment_date", sqlalchemy.Date)
    declared_date = sqlalchemy.Column("declared_date", sqlalchemy.Date)
    record_date = sqlalchemy.Column("record_date", sqlalchemy.Date)
    last_buy_date = sqlalchemy.Column("last_buy_date", sqlalchemy.Date)
    yield_value = sqlalchemy.Column("yield_value", DOUBLE)

    __table__ = sqlalchemy.Table(
        __tablename__,
        Base.metadata,
        ID,
        security_id,
        div_value,
        payment_date,
        declared_date,
        record_date,
        last_buy_date,
        yield_value
    )

    def get_table(self):
        return self.__table__

    def get_name(self):
        return self.__tablename__


class SecuritiesHistoryTable(Base):
    __tablename__ = "securities_history"

    security_id = sqlalchemy.Column("security_id", sqlalchemy.Integer,
                                    nullable=False,  primary_key=True)
    price = sqlalchemy.Column("price", DOUBLE)
    info_time = sqlalchemy.Column("info_time", sqlalchemy.DateTime,
                                  nullable=False, primary_key=True)
    volume = sqlalchemy.Column("volume", sqlalchemy.Integer)
    candle_interval = sqlalchemy.Column("candle_interval", sqlalchemy.Integer)

    __table__ = sqlalchemy.Table(
        __tablename__,
        Base.metadata,
        security_id,
        price,
        info_time,
        volume,
        candle_interval
    )

    def get_table(self):
        return self.__table__

    def get_name(self):
        return self.__tablename__
