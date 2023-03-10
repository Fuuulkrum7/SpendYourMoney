from datetime import datetime, timezone

from tinkoff.invest import MoneyValue

from database.database_info import SecuritiesHistory


class SecurityHistory:
    info_time: datetime
    price: float
    security_id: int
    volume: int

    def __init__(
            self,
            info_time: datetime = None,
            security_id: int = 0,
            price: float or MoneyValue = 0,
            volume: int = 1
    ):
        self.price = price
        self.security_id = security_id
        self.volume = volume
        self.info_time = info_time.replace(tzinfo=timezone.utc)

    def __contains__(self, item):
        return self.__eq__(item)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return other.price == self.price and \
            other.security_id == self.security_id and \
            other.info_time == other.info_time and \
            other.volume == self.volume

    def __hash__(self):
        return hash(
            (self.volume, self.price, self.security_id, self.info_time)
        )

    def __str__(self):
        return self.get_as_dict()

    def get_as_dict(self):
        return {
            SecuritiesHistory.security_id.value: self.security_id,
            SecuritiesHistory.price.value: self.price,
            SecuritiesHistory.volume.value: self.volume,
            SecuritiesHistory.info_time.value: self.info_time
        }
