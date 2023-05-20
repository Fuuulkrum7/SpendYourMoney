import os
from platform import system

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout

from info.file_loader import FileLoader


class Settings(QWidget):
    def __init__(self, app, settings, path):
        super().__init__()
        self.app = app
        self.settings = settings
        self.__path = path

        self.selected_theme = settings["theme"]
        self.selected_font = settings["font"]

        self.setWindowTitle("Settings")
        self.setFixedSize(200, 200)
        self.theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_list = ["Light", "Dark"]
        self.theme_combo.addItems(self.theme_list)
        self.theme_combo.setCurrentIndex(
            self.theme_list.index(self.selected_theme.capitalize()))
        self.theme_combo.currentIndexChanged.connect(self.on_theme_change)



        self.font_label = QLabel("Font:")
        self.font_combo = QComboBox()
        self.font_list = ["Default (system)", "Papyrus", "Comic Sans MS"]
        self.font_combo.addItems(self.font_list)
        self.font_combo.setCurrentIndex(
            self.font_list.index(self.selected_font))
        self.font_combo.currentIndexChanged.connect(self.on_font_change)


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.theme_label)
        self.layout.addWidget(self.theme_combo)
        self.layout.addWidget(self.font_label)
        self.layout.addWidget(self.font_combo)
        self.setLayout(self.layout)

        # sep = "\\" if system() == "Windows" else "/"
        # # Получаем путь до папки, где лежит файл
        # folder = os.path.abspath("security_info_tabs.py").split(sep)
        # # Удаляем папку, где лежит файл, из пути
        # folder.pop()
        # # Сохраняем его
        # self.__path = sep.join(folder)
        # self.settings = FileLoader.get_json(
        #     self.__path + "/info/files/.current_settings.json"
        # )
        # if self.settings is None:
        #     self.settings = FileLoader.get_json(
        #         self.__path + "/info/files/.default_settings.json"
        #     )
        #
        #     FileLoader.save_json(
        #         self.__path + "/info/files/.current_settings.json",
        #         self.settings
        #     )

    def on_theme_change(self, index):
        self.selected_theme = self.theme_list[index].lower()
        with open(f"ui_dev/{self.selected_theme}.css",
                  "r") as theme:
            self.app.setStyleSheet(theme.read())

        self.save_data()
        print(self.settings, "from theme")

    def on_font_change(self, index):
        self.selected_font = self.font_list[index]
        if index:
            self.qfont = QFont(self.selected_font)
        else:
            self.qfont = QFont()
        self.app.setFont(self.qfont)

        self.save_data()
        print(self.settings, "from font")

    def save_data(self):
        self.settings["theme"] = self.selected_theme
        self.settings["font"] = self.selected_font

        FileLoader.save_json(
            self.__path + "/info/files/.current_settings.json",
            self.settings
        )

def set_theme_and_font(app, settings):
    selected_theme = settings["theme"]
    selected_font = settings["font"]
    with open(f"ui_dev/{selected_theme}.css",
              "r") as theme:
        app.setStyleSheet(theme.read())

    if selected_font != "Default (system)":
        qfont = QFont(selected_font)
    else:
        qfont = QFont()
    app.setFont(qfont)
    print(settings, "from set")
