import asyncio
from datetime import timedelta

from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.utils import now

TOKEN = "t.0GnEOB1p5ODjob-f4qhnvbf2xgH1Up6ORFTOfiVKjd7EP4g_SkM8lQWX4Cins9fHNnb3oBqS4dzwQGBt1t7XVA"


async def main():
    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
            figi="BBG004730N88",
            from_=now() - timedelta(minutes=1),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            print(candle)


"""
def main():
    with Client(TOKEN) as client:
        r = client.instruments.find_instrument(query="газ")
        for i in r.instruments:
            if i.instrument_type == "bond":
                print(i)
"""

if __name__ == "__main__":
    asyncio.run(main())
