from abc import ABC, abstractmethod
import function

from threading import Thread
from securities.securities import SecurityInfo


class StandardQuery:
    """
    Стандартизированный поисковый запрос
    мы можем искать по любому полю из security_info. Или, если мы не знаем,
    по какому полю искать, храним текст запроса
    """
    security_info: SecurityInfo
    query_text: str

    def __init__(self, info: SecurityInfo, query_text: str):
        self.security_info = info
        self.query_text = query_text

    def get_query(self) -> str:
        # В первую очередь проверяем фиги
        if self.security_info.figi:
            return self.security_info.figi
        # потом тикер
        if self.security_info.ticker:
            return self.security_info.ticker
        # потом имя
        if self.security_info.name:
            return self.security_info.name
        # и в самом худшем случае текст
        return self.query_text


class SecurityGetter(ABC, Thread):
    # тело запроса
    query: StandardQuery
    # проверять ли данные локально
    check_locally: bool
    # добавлять ли данных
    insert_to_db: bool
    # функция, вызываемая по окончании работы геттера
    on_finish: function = None

    # Функция для загрузки данных в целом. То есть, со
    # всей внутренней логикой и проверкой
    @abstractmethod
    def load_data(self):
        pass

    # Метод добавления данных в бд.
    # Чтобы можно было вызвать откуда угодно в случае чего. Только в потоке!
    @abstractmethod
    def insert_to_database(self):
        pass

    # Метод для получения данных в бд
    @abstractmethod
    def get_from_bd(self):
        pass

    # и через апи
    @abstractmethod
    def get_from_api(self):
        pass
