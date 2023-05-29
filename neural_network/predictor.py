"""
Здесь лежит класс для работы с нейросетью
"""
from datetime import timedelta, timezone

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from keras.models import load_model
from tinkoff.invest import CandleInterval
from tinkoff.invest.utils import now

from api_requests.get_security_history import GetSecurityHistory
from neural_network.data_preparation import normalize_data
from securities.securities import Stock


class PredictCourse(QThread):
    """
    This class is used for making prediction of securities course using neural
    network. In fact, it is not perfect in such predictions, but it is not bad.
    Status-codes:
    200 - everything is ok
    250 - data can be not up-to-date, data is not actual
    """
    # Интересно, что же это такое... Даже не знаю
    status_code: int = 200
    # Текущая цб
    stock: Stock
    data_downloaded = pyqtSignal(object)
    # Результат работы модели
    result: list = []
    # Загруженная история
    history: list = []

    def __init__(self, stock: Stock, on_finish, token):
        super().__init__()
        self.securities_thread = None
        self.stock = stock
        self.data_downloaded.connect(on_finish)
        self.__token = token
        self.to = now() - timedelta(days=1)
        self.to = self.to.replace(tzinfo=timezone.utc)

    def run(self) -> None:
        # Запускаем поток по загрузке свечи
        self.securities_thread = GetSecurityHistory(
            info=self.stock.info,
            _from=now() - timedelta(days=1001),
            to=self.to,
            interval=CandleInterval.CANDLE_INTERVAL_DAY,
            token=self.__token,
            on_finish=self.on_load
        )

        self.securities_thread.start()

    def predict(self):
        # Если история успешно скачана
        if self.status_code < 300:
            try:
                # Загружаем сетку
                model = load_model("neural_network/model_best.keras")

                # Парсим данные по свечам в словари
                parsed = [i.get_as_dict() for i in self.history]
                # И удаляем индексы цб
                for i in parsed:
                    i.pop("security_id")

                # Получаем цб в виде словаря
                security = self.stock.get_as_dict()
                security.update(self.stock.get_as_dict_security())

                # Добавляем к цб историю
                security["history"] = parsed

                # Нормализуем данные
                norm = normalize_data({"data": security})[0]

                # Делаем предсказание по последним 120 свечам
                self.result = model.predict(norm[:, -120:])[0] * 100

                # Округляем результат
                self.result = list(np.around(self.result, decimals=2))
            except Exception as e:
                print(e)
                self.status_code = 500

        # Отправляем данные
        self.data_downloaded.emit((self.status_code, self.result))

    def on_load(self, result):
        # Сохраняем массив свечей
        code, self.history = result

        # Если данных по сути нет, массив пуст,
        # то прерываем работу
        if code == 500 or code == 300:
            self.status_code = 400

        # Если данных недостаточно для предсказания
        elif len(self.history) < 120:
            self.status_code = 300

        # Если выбранная дата не является текущей
        # и была ошибка при поиске цб в инете,
        # то есть вероятность, что предсказание будет не актуальным,
        # то есть без учета актуального курса
        elif code == 400 and self.history[-1].info_time.date() < \
                self.to.date():
            self.status_code = 250

        self.predict()
