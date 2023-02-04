CREATE TABLE IF NOT EXISTS user_table (
    UID INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(25),
    token CHAR(200),
    password CHAR(129),
    status INT,
    access_level INT,
    PRIMARY KEY(UID)
);

CREATE TABLE IF NOT EXISTS securities_info (
    ID INT NOT NULL AUTO_INCREMENT,
    figi CHAR(14),
    ticker CHAR(15),
    security_name CHAR(30),
    class_code CHAR(10),
    lot INT,
    currency CHAR(5),
    country VARCHAR(35),
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
    issue_size INT,
    stock_type INT,
    otc_flag BOOLEAN,
    div_yield_flag BOOLEAN,
    PRIMARY KEY(ID)
);

CREATE TABLE IF NOT EXISTS dividend_info (
    ID INT NOT NULL AUTO_INCREMENT,
    security_id INT,
    div_value DATE,
    payment_date DATE,
    declared_date DATE,
    record_date DATE,
    last_buy_date DATE,
    yield_value DOUBLE,
    PRIMARY KEY(ID)
);

CREATE TABLE IF NOT EXISTS securities_history (
    security_id INT,
    price DOUBLE,
    `time` DATETIME,
    volume INT
);

CREATE TABLE IF NOT EXISTS history_of_predictions (
    security_id INT,
    price DOUBLE,
    `time` DATETIME
);