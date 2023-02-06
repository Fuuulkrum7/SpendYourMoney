import asyncio
from datetime import timedelta
import threading

from database.database_interface import DatabaseInterface
from api_requests.securities_api import GetSecurity, SecurityInfo
from api_requests.security_getter import StandardQuery
from info.info import Info, User, Theme

from tinkoff.invest import CandleInterval, AsyncClient, Client
from tinkoff.invest.utils import now


TOKEN = "t.0GnEOB1p5ODjob-f4qhnvbf2xgH1Up6ORFTOfiVKjd7EP4g_SkM8lQWX4Cins9fHNnb3oBqS4dzwQGBt1t7XVA"


def init_db():
    db = DatabaseInterface()
    db.connect_to_db()


"""
async def main():
    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
            figi="BBG006L8G4H1",
            from_=now() - timedelta(days=365),
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
        ):
            print(candle)


th = threading.Thread(target=init_db)
th.start()

print("hello")
"""
async def main():
    with Client(TOKEN) as client:
        r = client.instruments.find_instrument(query=" ")
        for i in r.instruments:
            print(i)
        print(len(list(filter(lambda x: x.instrument_type in ["bond"], r.instruments))))


print("start")
s = GetSecurity(
    StandardQuery(
        SecurityInfo(
            0,
            "BBG006L8G4H1",
            "",
            ""
        ),
        ""
    ),
    lambda: print("done"),
    TOKEN
)
s.start()

if __name__ == "__main__":
    # asyncio.run(main())
    pass
