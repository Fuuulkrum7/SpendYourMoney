"""
Модуль с классом окна настроек
"""
import os

from PyQt5.QtCore import QFile, QByteArray
from PyQt5.QtGui import QFontDatabase, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout
from info.file_loader import FileLoader


class Settings(QWidget):
    """
    Класс применения настроек к интерфейсу
    """
    WIDTH = 200
    HEIGHT = 200

    def __init__(self, app, settings, path, hse_label):
        super().__init__()
        self.content = None
        self.app = app
        self.settings = settings
        self.__path = path
        self.hse_label = hse_label

        self.selected_theme = settings["theme"]
        self.selected_font = settings["font"]
        self.selected_size = settings["size"]

        self.setWindowTitle("Settings")

        screen = self.app.desktop().screenGeometry()
        self.setGeometry((screen.width() - self.WIDTH) // 2,
                         (screen.height() - self.HEIGHT) // 2,
                         self.WIDTH, self.HEIGHT)
        self.setFixedSize(self.WIDTH, self.HEIGHT)

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
        self.add_fonts_from_folder()
        self.font_combo.addItems(self.font_list)
        try:
            self.font_combo.setCurrentIndex(
                self.font_list.index(self.selected_font))
        except ValueError:
            self.font_combo.setCurrentIndex(0)
        self.font_combo.currentIndexChanged.connect(self.on_font_change)

        self.size_label = QLabel("Size:")
        self.size_combo = QComboBox()
        self.size_list = ["Default"]+[str(i) for i in range(8, 19)]
        self.size_combo.addItems(self.size_list)
        self.size_combo.setCurrentIndex(
            self.size_list.index(self.selected_size))
        self.size_combo.currentIndexChanged.connect(self.on_size_change)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.theme_label)
        self.layout.addWidget(self.theme_combo)
        self.layout.addWidget(self.font_label)
        self.layout.addWidget(self.font_combo)
        self.layout.addWidget(self.size_label)
        self.layout.addWidget(self.size_combo)
        self.setLayout(self.layout)

    def add_fonts_from_folder(self):
        """
        Обнаружение пользовательских шрифтов в папке
        """
        folder = "info/files/fonts"
        for filename in os.listdir(folder):
            if filename.lower()[-4:] in ('.ttf', '.otf'):
                file = QFile("/".join((self.__path, folder, filename)))
                file.open(QFile.ReadOnly)
                font_data = file.readAll()
                file.close()

                # добавляем шрифт в базу данных шрифтов PyQt
                font_id = QFontDatabase.addApplicationFontFromData(
                    QByteArray(font_data))

                # получаем его имя
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                self.font_list.append(font_family)

    def get_css_content(self):
        """
        Сборка css из трех настроек
        """
        with open(f"ui_dev/visual_settings/{self.selected_theme}.css",
                  "r") as theme:
            css_theme = theme.read()

        if self.selected_font != "Default (system)":
            css_font = f'* {{font-family: "{self.selected_font}";}}'
        else:
            css_font = ''

        if self.selected_size != "Default":
            css_size = f'* {{font-size: {self.selected_size}pt;}}'
            print(css_size)
        else:
            css_size = ''

        return css_theme + css_font + css_size

    def on_theme_change(self, index):
        """
        Смена темы
        """
        self.selected_theme = self.theme_list[index].lower()
        self.save_data()
        self.content = self.get_css_content()
        self.app.setStyleSheet(self.content)

        if "hse" in self.selected_font.lower().split():
            pixmap = QPixmap(self.__path + f"/info/files/HSE_"
                                           f"{self.selected_theme}.png")
            self.hse_label.setPixmap(pixmap)

    def on_font_change(self, index):
        """
        Смена шрифта
        """
        self.selected_font = self.font_list[index]
        self.save_data()
        self.content = self.get_css_content()
        self.app.setStyleSheet(self.content)

        self.hse_label.setVisible("hse" in self.selected_font.lower().split())

    def on_size_change(self, index):
        """
        Смена размера шрифта
        """
        self.selected_size = self.size_list[index]
        self.save_data()
        self.content = self.get_css_content()
        self.app.setStyleSheet(self.content)

    def save_data(self):
        """
        Сохранение всех настроек
        """
        self.settings["theme"] = self.selected_theme.lower()
        self.settings["font"] = self.selected_font
        self.settings["size"] = self.selected_size

        FileLoader.save_json(
            self.__path + "/info/files/.current_settings.json",
            self.settings
        )


def set_theme_and_font(app, settings, path, label):
    """
    Применение всех настроек при открытии приложения
    """
    initial = Settings(app, settings, path, label)
    initial.add_fonts_from_folder()
    content = initial.get_css_content()
    app.setStyleSheet(content)
