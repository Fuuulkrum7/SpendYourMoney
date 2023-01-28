import asyncio
from datetime import timedelta

from database.database_interface import DatabaseInterface

from tinkoff.invest import CandleInterval, AsyncClient, Client
from tinkoff.invest.utils import now

TOKEN = "t.0GnEOB1p5ODjob-f4qhnvbf2xgH1Up6ORFTOfiVKjd7EP4g_SkM8lQWX4Cins9fHNnb3oBqS4dzwQGBt1t7XVA"


async def main():
    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
            figi="BBG0027F0Y27",
            from_=now() - timedelta(hours=1),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR,
        ):
            print(candle)

db = DatabaseInterface("any")
"""
async def main():
    with Client(TOKEN) as client:
        r = client.instruments.find_instrument(query="")
        for i in r.instruments:
            print(i)
"""


if __name__ == "__main__":
    asyncio.run(main())
