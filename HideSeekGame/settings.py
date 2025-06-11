# settings.py

class GameSettings:
    def __init__(self):
        self.theme_name = "Dark"
        self.themes = {
            "Dark": {"bg": (20, 20, 20), "player": (255, 255, 255), "seeker_easy": (255, 0, 0), "seeker_hard": (0, 0, 255)},
            "Red": {"bg": (100, 0, 0), "player": (255, 255, 255), "seeker_easy": (255, 255, 0), "seeker_hard": (0, 255, 255)},
            "White": {"bg": (240, 240, 240), "player": (0, 0, 0), "seeker_easy": (255, 0, 0), "seeker_hard": (0, 0, 255)}
        }
        self.difficulty = "Easy"

    @property
    def theme(self):
        return self.themes[self.theme_name]

    def next_theme(self):
        keys = list(self.themes.keys())
        idx = (keys.index(self.theme_name) + 1) % len(keys)
        self.theme_name = keys[idx]

    def previous_theme(self):
        keys = list(self.themes.keys())
        idx = (keys.index(self.theme_name) - 1) % len(keys)
        self.theme_name = keys[idx]

    def toggle_difficulty(self):
        self.difficulty = "Hard" if self.difficulty == "Easy" else "Easy"