class Theme:
    primary_color: str
    primary_light_color: str
    primary_dark_color: str
    secondary_color: str
    secondary_light_color: str
    secondary_dark_color: str

    def get_theme_as_dict(self) -> dict:
        return {
            "primary_color": self.primary_color,
            "primary_light_color": self.primary_light_color,
            "primary_dark_color": self.primary_dark_color,
            "secondary_color": self.secondary_color,
            "secondary_light_color": self.secondary_light_color,
            "secondary_dark_color": self.secondary_dark_color
        }
