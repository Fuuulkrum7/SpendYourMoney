import asyncio
from datetime import timedelta

from database.database_interface import DatabaseInterface

from tinkoff.invest import CandleInterval, AsyncClient, Client
from tinkoff.invest.utils import now

TOKEN = "t.0GnEOB1p5ODjob-f4qhnvbf2xgH1Up6ORFTOfiVKjd7EP4g_SkM8lQWX4Cins9fHNnb3oBqS4dzwQGBt1t7XVA"


async def main():
    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
            figi="BBG006L8G4H1",
            from_=now() - timedelta(minutes=10),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            print(candle)

db = DatabaseInterface("any")
"""
async def main():
    with Client(TOKEN) as client:
        r = client.instruments.find_instrument(query=" ")
        for i in r.instruments:
            print(i)
        print(len(list(filter(lambda x: x.instrument_type in ["bond"], r.instruments))))
"""


if __name__ == "__main__":
    asyncio.run(main())
