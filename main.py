from datetime import timedelta

from preinstall import installation

try:
    import cryptography
    import sqlalchemy
    import MySQLdb
    from tinkoff.invest import CandleInterval, AsyncClient, Client
    from tinkoff.invest.utils import now
except ImportError:
    installation(["tinkoff-investments",
                  "SQLAlchemy<2.0.0", "SQLAlchemy-Utils",
                  "function", "pymysql", "cryptography",
                  "mysqlclient"])
    import cryptography
    from tinkoff.invest import CandleInterval, AsyncClient, Client
    from tinkoff.invest.utils import now


from securities.securities import SecurityInfo
from api_requests.security_getter import StandardQuery
from api_requests.get_security import GetSecurity


TOKEN = "t.0GnEOB1p5ODjob-f4qhnvbf2xgH1Up6ORFTO" \
        "fiVKjd7EP4g_SkM8lQWX4Cins9fHNnb3oBqS4dzwQGBt1t7XVA"


async def main():
    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
            figi="BBG006L8G4H1",
            from_=now() - timedelta(days=1),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            print(candle)


print("start")
s = GetSecurity(
    StandardQuery(
        SecurityInfo(
            id=0,
            figi="",
            security_name="",
            ticker="",
            class_code=""
        ),
        " "
    ),
    lambda x: print("done, status: ", x),
    TOKEN
)
s.start()

if __name__ == "__main__":
    # asyncio.run(main())
    pass
