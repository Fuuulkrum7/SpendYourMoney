import asyncio
from datetime import timedelta

from api_requests.securities_api import GetSecurity, SecurityInfo
from api_requests.security_getter import StandardQuery

from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.utils import now


TOKEN = "t.0GnEOB1p5ODjob-f4qhnvbf2xgH1Up6ORFTOfiVKjd7EP4g_SkM8lQWX4Cins9fHNnb3oBqS4dzwQGBt1t7XVA"


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
        "US31620R3030"
    ),
    lambda x: print("done, status: ", x),
    TOKEN
)
s.start()

if __name__ == "__main__":
    # asyncio.run(main())
    pass
