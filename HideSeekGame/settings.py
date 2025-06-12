from config import THEMES

class Settings:
    def __init__(self):
        self.theme_index = 0
        self.theme_name = list(THEMES.keys())[self.theme_index]
        self.difficulty = "Easy"
        self.high_score = 0

    def toggle_difficulty(self):
        if self.difficulty == "Easy":
            self.difficulty = "Hard"
        elif self.difficulty == "Hard":
            self.difficulty = "Master"
        else:
            self.difficulty = "Easy"

    def next_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        self.theme_name = list(THEMES.keys())[self.theme_index]

    def get_theme(self):
        return THEMES[self.theme_name]

    def get_difficulty_desc(self):
        if self.difficulty == "Easy":
            return "Easy: Slow seekers, long boost, obstacles move every 35s."
        elif self.difficulty == "Hard":
            return "Hard: Faster seekers, shorter boost, obstacles move every 35s."
        else:
            return "Master: Seekers very fast, obstacles never move!"

    def get_seeker_speed(self):
        from config import SEEKER_SPEEDS
        return SEEKER_SPEEDS[self.difficulty]

    def get_seeker_spawn_interval(self):
        from config import SEEKER_SPAWN_INTERVALS
        return SEEKER_SPAWN_INTERVALS[self.difficulty]

    def get_boost_duration(self):
        from config import BOOST_DURATION
        return BOOST_DURATION[self.difficulty]

    def get_projectile_cooldown(self):
        from config import PROJECTILE_COOLDOWNS
        return PROJECTILE_COOLDOWNS[self.difficulty]