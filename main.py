import asyncio
from datetime import timedelta

from api_requests.get_security_history import GetSecurityHistory
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


TOKEN = "t.0GnEOB1p5ODjob-f4qhnvbf2xgH1Up6ORFTO" \
        "fiVKjd7EP4g_SkM8lQWX4Cins9fHNnb3oBqS4dzwQGBt1t7XVA"


async def main():
    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
            figi="BBG006L8G4H1",
            from_=now() - timedelta(minutes=5),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            print(candle)


def load_securities(x):
    print(*[val.get_as_dict_security() for val in s.securities],
          sep='\n')

    res = GetSecurityHistory(
        info=s.securities[0].info,
        _from=now() - timedelta(minutes=5),
        to=now(),
        interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        token=TOKEN,
        on_finish=lambda n: print(
            *[val.get_as_dict() for val in res.history],
            sep='\n'
        )
    )

    res.start()


print("start")

"""
s = LoadAllSecurities(
    lambda x: print(f"done, code = {x}"),
    TOKEN
)

"""
s = GetSecurity(
    StandardQuery(
        SecurityInfo(
            id=0,
            figi="",
            security_name="",
            ticker="",
            class_code=""
        ),
        "LKOH"
    ),
    load_securities,
    TOKEN
)
s.start()

sec = SecurityHistory()


if __name__ == "__main__":
    # asyncio.run(main())
    pass
