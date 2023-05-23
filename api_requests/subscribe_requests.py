import time

from PyQt5.QtCore import QThread, pyqtSignal
from tinkoff.invest import MarketDataRequest, SubscribeCandlesRequest, \
    SubscriptionAction, CandleInstrument, SubscriptionInterval, Client, \
    RequestError

from securities.securities import Security, SecurityInfo
from securities.securities_history import SecurityHistory


class SubscribeOnMarket(QThread):
    """
    Class, using which we create actual price of securities in real time
    Important - we have only ended candles.
    Status codes:
    200 - success
    400 - standard error, occurred during data load, troubles with network
    500 - we don't know, what have happened, but we've got an error
    """
    status_code: int = 200
    # Вид подписки
    subscription: SubscriptionAction
    # Интервал подписки
    interval: SubscriptionInterval
    # ЦБ
    security: SecurityInfo

    data_downloaded = pyqtSignal(object)

    def __init__(self, security: SecurityInfo,
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
            # Генератор, который делает запросы на рынок с задержкой 1 секунду
            yield MarketDataRequest(
                subscribe_candles_request=SubscribeCandlesRequest(
                    waiting_close=True,
                    subscription_action=self.subscription,
                    instruments=[
                        CandleInstrument(
                            figi=self.security.figi,
                            interval=self.interval,
                        )
                    ],
                )
            )
            while True:
                time.sleep(1)
        try:
            # Создаем подключение
            with Client(self.__token) as client:
                # Теперь перебираем генератор
                for marketdata in client.market_data_stream.market_data_stream(
                        request_iterator()
                ):
                    # Получаем свечу
                    candle = marketdata.candle
                    # Если она есть (торги были за выбранный временной
                    # промежуток), то создаем свечу
                    # и отправляем ее в функцию
                    if candle is not None:
                        history = SecurityHistory(
                            info_time=candle.time,
                            volume=candle.volume,
                            price=candle.close,
                            security_id=self.security.info.id
                        )

                        self.data_downloaded.emit((self.status_code, history))
        except RequestError as e:
            # Ошибка подключения
            print("Error in request\n", e)
            self.status_code = 400
        except Exception as e:
            # Рандомная бяка
            print("Error unknown\n", e)
            self.status_code = 500

        self.data_downloaded.emit((self.status_code, []))

    def stop(self):
        # Останавливаем таким образом генератор
        self.subscription = SubscriptionAction.SUBSCRIPTION_ACTION_UNSUBSCRIBE
