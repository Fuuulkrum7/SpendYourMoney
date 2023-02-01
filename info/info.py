from info.user import User
from info.theme import Theme


class Info:
    """
     В данном классе хранятся основные данные, такие как данные пользователя,
     настройки и тп
    """
    user: User
    theme: Theme
    path: str

    def __init__(self, user: User, theme: Theme, path: str):
        self.user = user
        self.theme = theme
        self.path = path
