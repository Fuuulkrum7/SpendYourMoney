CREATE TABLE IF NOT EXISTS user_table (
    UID INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(25),
    token VARCHAR(200),
    password VARCHAR(129),
    status INT,
    access_level INT,
    PRIMARY KEY(UID)
);

CREATE TABLE IF NOT EXISTS securities_info (
    ID INT NOT NULL AUTO_INCREMENT,
    figi VARCHAR(14) NOT NULL,
    ticker VARCHAR(15),
    security_name VARCHAR(100),
    class_code VARCHAR(18),
    lot INT,
    currency VARCHAR(5),
    country VARCHAR(70),
    country_code VARCHAR(8),
    sector VARCHAR(30),
    security_type TINYINT,
    priority TINYINT DEFAULT 0,
    PRIMARY KEY(ID),
    UNIQUE (figi)
);

CREATE TABLE IF NOT EXISTS bonds_info (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT NOT NULL,
    coupon_quantity_per_year INT,
    maturity_date DATE,
    nominal DOUBLE,
    aci_value DOUBLE,
    issue_size BIGINT,
    issue_size_plan BIGINT,
    floating_coupon_flag BOOLEAN,
    perpetual_flag BOOLEAN,
    amortization_flag BOOLEAN,
    PRIMARY KEY(ID),
    UNIQUE (security_id)
);

CREATE TABLE IF NOT EXISTS coupon_info (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT NOT NULL,
    coupon_date DATE,
    coupon_number INT,
    fix_date DATE NOT NULL,
    pay_one_bond DOUBLE,
    coupon_type INT,
    PRIMARY KEY(ID),
    CONSTRAINT UC_coup UNIQUE (security_id, coupon_date)
);

CREATE TABLE IF NOT EXISTS stocks_info (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT NOT NULL,
    ipo_date DATE,
    issue_size BIGINT,
    stock_type SMALLINT,
    otc_flag BOOLEAN,
    div_yield_flag BOOLEAN,
    PRIMARY KEY(ID),
    UNIQUE (security_id)
);

CREATE TABLE IF NOT EXISTS dividend_info (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT NOT NULL,
    div_value DOUBLE,
    payment_date DATE NOT NULL,
    declared_date DATE,
    record_date DATE,
    last_buy_date DATE,
    yield_value DOUBLE,
    PRIMARY KEY(ID),
    CONSTRAINT UC_div UNIQUE (security_id, declared_date, div_value)
);

CREATE TABLE IF NOT EXISTS securities_history (
    security_id INT NOT NULL,
    price DOUBLE,
    info_time DATETIME NOT NULL,
    volume BIGINT,
    candle_interval INT NOT NULL,
    CONSTRAINT UC_history PRIMARY KEY (security_id, info_time, candle_interval)
);

CREATE TABLE IF NOT EXISTS history_of_predictions (
    security_id INT,
    price DOUBLE,
    info_time DATETIME,
    CONSTRAINT UC_history PRIMARY KEY (security_id, info_time)
);
