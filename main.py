import os
from datetime import timedelta

from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now

TOKEN = "t.0GnEOB1p5ODjob-f4qhnvbf2xgH1Up6ORFTOfiVKjd7EP4g_SkM8lQWX4Cins9fHNnb3oBqS4dzwQGBt1t7XVA"


def main():
    with Client(TOKEN) as client:
        for candle in client.get_all_candles(
            figi="BBG004731032",
            from_=now() - timedelta(minutes=60),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR,
        ):
            print(candle)

    return 0


if __name__ == "__main__":
    main()
