from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout


class Settings(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle("Settings")
        self.setFixedSize(200, 200)
        self.theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.themes_list = ["Light", "Dark"]
        self.theme_combo.addItems(self.themes_list)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_change)

        self.font_label = QLabel("Font:")
        self.font_combo = QComboBox()
        self.fonts_list = ["Default (system)", "Papyrus", "Comic Sans MS"]
        self.font_combo.addItems(self.fonts_list)
        self.font_combo.currentIndexChanged.connect(self.on_font_change)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.theme_label)
        self.layout.addWidget(self.theme_combo)
        self.layout.addWidget(self.font_label)
        self.layout.addWidget(self.font_combo)
        self.setLayout(self.layout)

    def on_theme_change(self, index):
        with open(f"ui_dev/{self.themes_list[index].lower()}.css",
                  "r") as theme:
            self.app.setStyleSheet(theme.read())

    def on_font_change(self, index):
        if index:
            self.font = QFont(self.fonts_list[index])
        else:
            self.font = QFont()
        self.app.setFont(self.font)
