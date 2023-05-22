from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout

from info.file_loader import FileLoader


class Settings(QWidget):
    def __init__(self, app, settings, path):
        super().__init__()
        self.content = None
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

    def get_css_content(self):
        with open(f"ui_dev/visual_settings/{self.selected_theme}.css",
                  "r") as theme:
            css_theme = theme.read()

        if self.selected_font != "Default (system)":
            css_font = f'* {{font-family: "{self.selected_font}";}}'
        else:
            css_font = ''
        return css_theme + css_font

    def on_theme_change(self, index):
        self.selected_theme = self.theme_list[index].lower()
        self.save_data()
        self.content = self.get_css_content()
        self.app.setStyleSheet(self.content)
        print(self.content, "from theme")

    def on_font_change(self, index):
        self.selected_font = self.font_list[index]
        self.save_data()
        self.content = self.get_css_content()
        self.app.setStyleSheet(self.content)
        print(self.content, "from font")

    def save_data(self):
        self.settings["theme"] = self.selected_theme.lower()
        self.settings["font"] = self.selected_font

        FileLoader.save_json(
            self.__path + "/info/files/.current_settings.json",
            self.settings
        )


def set_theme_and_font(app, settings):
    selected_theme = settings["theme"]
    selected_font = settings["font"]
    with open(f"ui_dev/visual_settings/{selected_theme}.css",
              "r") as theme:
        css_theme = theme.read()

    if selected_font != "Default (system)":
        css_font = f'* {{font-family: "{selected_font}";}}'
    else:
        css_font = ''
    app.setStyleSheet(css_theme + css_font)
    print(css_theme + css_font, "from set")
