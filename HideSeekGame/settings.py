# settings.py

from config import THEMES

class Settings:
    def __init__(self):
        self.theme_index = 0
        self.theme_name = list(THEMES.keys())[self.theme_index]
        self.difficulty = "Easy"
        self.high_score = 0

    def toggle_difficulty(self):
        self.difficulty = "Hard" if self.difficulty == "Easy" else "Easy"

    def next_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        self.theme_name = list(THEMES.keys())[self.theme_index]

    def get_theme(self):
        return THEMES[self.theme_name]