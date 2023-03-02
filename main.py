from datetime import timedelta

from api_requests.get_security_history import GetSecurityHistory
from info.user import User
from preinstall import installation
from securities.securities_history import SecurityHistory

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


from securities.securities import SecurityInfo
from api_requests.security_getter import StandardQuery
from api_requests.get_security import GetSecurity
from api_requests.load_all_securities import LoadAllSecurities
from api_requests.user_methods import CheckUser, CreateUser


# TOKEN = "t.0GnEOB1p5ODjob-f4qhnvbf2xgH1Up6ORFTOfiVKj
# d7EP4g_SkM8lQWX4Cins9fHNnb3oBqS4dzwQGBt1t7XVA"

user: User = None


def main():
    """
    s = LoadAllSecurities(
        lambda x: print(f"done, code = {x}"),
        TOKEN
    )

    """

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
        lambda x, y: print("done, code = ",
                           x,
                           "data: ",
                           *([i.get_as_dict_security() for i in y]),
                           sep='\n'),
        user.get_token()
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
    if code == 200:
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


"""
def load_securities(x):
    print(*[val.get_as_dict_security() for val in s.securities],
          sep='\n')

    res = GetSecurityHistory(
        info=s.securities[0].info,
        _from=now() - timedelta(minutes=5),
        to=now(),
        interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        token=user.get_token(),
        on_finish=lambda n: print(
            *[val.get_as_dict() for val in res.history],
            sep='\n'
        )
    )

    res.start()
"""


print("start")

login = input("Enter login\n")
password = input("Enter password\n")

CheckUser(
    login,
    password,
    create_user
).start()
