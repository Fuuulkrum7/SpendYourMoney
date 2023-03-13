from datetime import datetime, timezone

from tinkoff.invest import MoneyValue, CandleInterval

from database.database_info import SecuritiesHistory


class SecurityHistory:
    """
    Класс, содержащий внутри себя данные о стоимости цб в конкретный
    момент времени
    """
    # момент времени
    info_time: datetime
    # цена в этот момент времени
    price: float
    # id нашей цб
    security_id: int
    # объем торгов
    volume: int

    def __init__(
            self,
            info_time: datetime = None,
            security_id: int = 0,
            price: float or MoneyValue = 0,
            volume: int = 1,
            candle_interval: CandleInterval =
            CandleInterval.CANDLE_INTERVAL_UNSPECIFIED
    ):
        # парсим данные по полям
        # candle_interval - защита от ошибок
        self.price = price
        self.security_id = security_id
        self.volume = volume
        self.info_time = info_time.replace(tzinfo=timezone.utc)

    # Для проверки на равенство
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return other.price == self.price and \
            other.security_id == self.security_id and \
            other.info_time == self.info_time and \
            other.volume == self.volume

    # И работы с множествами
    def __hash__(self):
        return hash(
            (self.security_id, self.info_time, self.volume)
        )

    def __str__(self):
        return str(self.get_as_dict())

    def __repr__(self):
        return self.__str__()

    def get_as_dict(self):
        return {
            SecuritiesHistory.security_id.value: self.security_id,
            SecuritiesHistory.price.value: self.price,
            SecuritiesHistory.volume.value: self.volume,
            SecuritiesHistory.info_time.value: self.info_time
        }

    # Метод нужен для более удобного добавления данных в бд
    def get_as_dict_candle(self, candle: CandleInterval) -> dict:

        return {
            SecuritiesHistory.security_id.value: self.security_id,
            SecuritiesHistory.price.value: self.price,
            SecuritiesHistory.volume.value: self.volume,
            SecuritiesHistory.info_time.value: self.info_time,
            SecuritiesHistory.CANDLE_INTERVAL.value: candle.value
        }
