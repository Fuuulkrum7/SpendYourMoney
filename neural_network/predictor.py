from datetime import timedelta

from PyQt5.QtCore import QThread, pyqtSignal
from keras.models import load_model
from tinkoff.invest import CandleInterval
from tinkoff.invest.utils import now

from api_requests.get_security_history import GetSecurityHistory
from neural_network.data_preparation import normalize_data
from securities.securities import Stock


class PredictCourse(QThread):
    # Интересно, что же это такое... Даже не знаю
    status_code: int = 200
    stock: Stock
    data_downloaded = pyqtSignal(object)
    result: list
    history: list

    def __init__(self, stock: Stock, on_finish, token):
        super().__init__()
        self.securities_thread = None
        self.stock = stock
        self.data_downloaded.connect(on_finish)
        self.__token = token

    def run(self) -> None:
        self.load_history()
        self.securities_thread.wait()

        if self.status_code != 200:
            return

        try:
            model = load_model("neural_network/model_best.keras")

            parsed = [i.get_as_dict() for i in self.history]
            for i in parsed:
                i.pop("security_id")

            security = self.stock.get_as_dict()
            security.update(self.stock.get_as_dict_security())

            security["history"] = parsed

            norm = normalize_data({"data": security})[0]

            self.result = model.predict(norm[:, -120:])

            self.data_downloaded.emit((self.status_code, self.result))
        except Exception as e:
            print(e)
            self.status_code = 500
            raise e

    def on_load(self, result):
        code, data = result
        if code != 200:
            self.status_code = 400
            return

        if len(data) < 120:
            self.status_code = 300
            return

        self.history = data

    def load_history(self):
        self.securities_thread = GetSecurityHistory(
                info=self.stock.info,
                _from=now() - timedelta(days=1001),
                to=now() - timedelta(days=1),
                interval=CandleInterval.CANDLE_INTERVAL_DAY,
                token=self.__token,
                on_finish=self.on_load
            )

        self.securities_thread.start()
