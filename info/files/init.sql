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
    figi VARCHAR(14),
    ticker VARCHAR(15),
    security_name VARCHAR(70),
    class_code VARCHAR(15),
    lot INT,
    currency VARCHAR(5),
    country VARCHAR(70),
    sector VARCHAR(30),
    security_type TINYINT,
    PRIMARY KEY(ID)
);

CREATE TABLE IF NOT EXISTS bonds_info (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT,
    coupon_quantity_per_year INT,
    maturity_date DATE,
    nominal DOUBLE,
    aci_value DOUBLE,
    issue_size INT,
    issue_size_plan INT,
    floating_coupon_flag BOOLEAN,
    perpetual_flag BOOLEAN,
    amortization_flag BOOLEAN,
    PRIMARY KEY(ID)
);

CREATE TABLE IF NOT EXISTS coupon_info (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT,
    coupon_date DATE,
    coupon_number INT,
    fix_date DATE,
    pay_one_bond DOUBLE,
    coupon_type INT,
    PRIMARY KEY(ID)
);

CREATE TABLE IF NOT EXISTS stocks_info (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT,
    ipo_date DATE,
    issue_size BIGINT,
    stock_type SMALLINT,
    otc_flag BOOLEAN,
    div_yield_flag BOOLEAN,
    PRIMARY KEY(ID)
);

CREATE TABLE IF NOT EXISTS dividend_info (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT,
    div_value DOUBLE,
    payment_date DATE,
    declared_date DATE,
    record_date DATE,
    last_buy_date DATE,
    yield_value DOUBLE,
    PRIMARY KEY(ID)
);

CREATE TABLE IF NOT EXISTS securities_history (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT,
    price DOUBLE,
    `time` DATETIME,
    volume INT,
    PRIMARY KEY(ID)
);

CREATE TABLE IF NOT EXISTS history_of_predictions (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT,
    price DOUBLE,
    `time` DATETIME,
    PRIMARY KEY(ID)
);
