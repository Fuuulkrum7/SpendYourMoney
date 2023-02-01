CREATE TABLE IF NOT EXISTS user_table (
    UID INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(25),
    token CHAR(200),
    password CHAR(129),
    status INT,
    access_level INT
);

CREATE TABLE IF NOT EXISTS securities_info (
    ID INT NOT NULL AUTO_INCREMENT,
    figi CHAR(14),
    ticker CHAR(15),
    name CHAR(30),
    class_code CHAR(10),
    lot INT,
    currency CHAR(5),
    country VARCHAR,
    sector VARCHAR
);