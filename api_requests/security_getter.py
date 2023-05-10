from abc import ABC, abstractmethod
import function

from PyQt5.QtCore import QThread as Thread
from securities.securities import SecurityInfo


class StandardQuery:
    """
    Стандартизированный поисковый запрос
    мы можем искать по любому полю из security_info. Или, если мы не знаем,
    по какому полю искать, храним текст запроса
    """
    security_info: SecurityInfo
    query_text: str

    def __init__(self, info: SecurityInfo,
                 query_text: str,
                 is_advanced = False):
        self.security_info = info
        self.query_text = query_text
        self.is_advanced = is_advanced

    def get_query(self) -> str:
        # В первую очередь проверяем фиги
        # потом тикер
        if self.security_info.figi:
            return  self.security_info.figi
        if self.security_info.ticker:
            return self.security_info.ticker
        # потом имя
        if self.security_info.name:
            return self.security_info.name
        if self.security_info.class_code:
            return self.security_info.class_code
        # и в самом худшем случае текст
        return self.query_text

    def get_figi(self):
        if self.is_advanced:
            if self.security_info.figi:
                return self.security_info.figi
            return  "@@@@@@@"
        return self.get_query()

    def get_ticker(self):
        if self.is_advanced:
            if self.security_info.ticker:
                return self.security_info.ticker
            return  "@@@@@@@"
        return self.get_query()

    def get_name(self):
        if self.is_advanced:
            if self.security_info.name:
                return self.security_info.name
            return  "@@@@@@@"
        return self.get_query()

    def get_class_code(self):
        if self.is_advanced:
            if self.security_info.class_code:
                return self.security_info.class_code
            return  "@@@@@@@"
        return self.get_query()


class SecurityGetter(Thread):
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

    # Метод получения загруженных данный
    def get_data(self):
        pass
