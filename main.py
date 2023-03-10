from datetime import timedelta
from preinstall import installation

try:
    import cryptography
    import sqlalchemy
    import pymysql
    from tinkoff.invest import CandleInterval, AsyncClient, Client
    from tinkoff.invest.utils import now
except ImportError:
    installation(["tinkoff-investments",
                  "SQLAlchemy<2.0.0", "SQLAlchemy-Utils",
                  "function", "cryptography",
                  "pymysql"])
    import cryptography
    from tinkoff.invest import CandleInterval, AsyncClient, Client
    from tinkoff.invest.utils import now


from api_requests.get_security_history import GetSecurityHistory
from api_requests.load_all_securities import LoadAllSecurities
from info.user import User
from securities.securities import SecurityInfo, Security
from api_requests.security_getter import StandardQuery
from api_requests.get_security import GetSecurity
from api_requests.user_methods import CheckUser, CreateUser


user: User = None


def on_finish(x, y: list[Security]):
    print("done, code = ",
          x,
          "data: ",
          *([i.get_as_dict() for i in y]),
          sep='\n'
          )
    for val in y:
        load_securities(val.info)


def main():
    """
    s = LoadAllSecurities(
        lambda x, y: print(f"done, code = {x}"),
        user.get_token()
    )

    """

    # В текущий момент мы ищем только локально
    data = input("Enter security name\n")
    s = GetSecurity(
        StandardQuery(
            SecurityInfo(
                id=0,
                figi="",
                security_name="",
                ticker="",
                class_code=""
            ),
            data
        ),
        on_finish,
        user.get_token(),
        load_coupons=False,
        load_dividends=False,
        load_full_info=False
    )
    s.start()


def after_create(code: int, loaded_data):
    global user
    if code == 200:
        print("success")
        user = loaded_data
        if __name__ == "__main__":
            main()
    else:
        print("error")


def create_user(code: int, loaded_data):
    global user
    print(code)
    if code == 200 or code == 211:
        user = loaded_data
        print("success login")
        main()
    elif code == 100:
        print("Некорректный логин или пароль")
    else:
        print(code)
        token = input("Увы, пользователя нет. Введите токен"
                      " для создания пользователя\n")
        create = CreateUser(
            User(
                token=token,
                username=login
            ),
            password,
            after_create
        )
        create.start()


def load_securities(info):
    res = GetSecurityHistory(
        info=info,
        _from=now() - timedelta(days=10),
        to=now(),
        interval=CandleInterval.CANDLE_INTERVAL_DAY,
        token=user.get_token(),
        on_finish=lambda n, y: print(
            *[val.get_as_dict() for val in res.history],
            sep='\n'
        )
    )

    res.start()


print("start")

login = input("Enter login\n")
password = input("Enter password\n")

CheckUser(
    login,
    password,
    create_user
).start()
