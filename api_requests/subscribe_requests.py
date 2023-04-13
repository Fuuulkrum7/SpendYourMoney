import time

from PyQt5.QtCore import QThread, pyqtSignal
from tinkoff.invest import MarketDataRequest, SubscribeCandlesRequest, \
    SubscriptionAction, CandleInstrument, SubscriptionInterval, Client

from securities.securities import Security
from securities.securities_history import SecurityHistory


class SubscribeOnMarket(QThread):
    subscription: SubscriptionAction
    interval: SubscriptionInterval
    security: Security

    data_downloaded = pyqtSignal(object)

    def __init__(self, security: Security,
                 token: str, on_finish,
                 subscription: SubscriptionAction =
                 SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                 interval: SubscriptionInterval =
                 SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE):
        super().__init__()

        self.interval = interval
        self.security = security
        self.subscription = subscription
        self.__token = token

        self.data_downloaded.connect(on_finish)

    def run(self) -> None:
        def request_iterator():
            yield MarketDataRequest(
                subscribe_candles_request=SubscribeCandlesRequest(
                    waiting_close=True,
                    subscription_action=self.subscription,
                    instruments=[
                        CandleInstrument(
                            figi=self.security.info.figi,
                            interval=self.interval,
                        )
                    ],
                )
            )
            while True:
                time.sleep(1)

        with Client(self.__token) as client:
            for marketdata in client.market_data_stream.market_data_stream(
                    request_iterator()
            ):
                candle = marketdata.candle
                if candle is not None:
                    history = SecurityHistory(
                        info_time=candle.time,
                        volume=candle.volume,
                        price=candle.close,
                        security_id=self.security.info.id
                    )

                    self.data_downloaded.emit((history, ))

    def stop(self):
        self.subscription = SubscriptionAction.SUBSCRIPTION_ACTION_UNSUBSCRIBE
