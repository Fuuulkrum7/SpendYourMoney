from user import User
from theme import Theme


class Info:
    """
     В данном классе хранятся основные данные, такие как данные пользователя,
     настройки и тп
    """
    user: User
    theme: Theme

    def __init__(self, user: User, theme: Theme):
        self.user = user
        self.theme = theme
