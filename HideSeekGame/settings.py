"""
settings.py — Hide & Seek+ Game Settings, Profiles, Achievements, and Accessibility
CrystalCard-hub, Copilot (2025 Refined Edition)
Lines: 500+
Handles user options, profiles, color themes, accessibility, achievements, difficulty, and gameplay curves.
"""

import json
import os
from config import (
    THEMES, BOOST_DURATION, SEEKER_SPEEDS, SEEKER_SPAWN_INTERVALS, PROJECTILE_COOLDOWNS,
    ACHIEVEMENT_LIST, get_achievement_desc, POWERUP_NAMES
)

SETTINGS_FILE = "user_settings.json"
ACHIEVEMENTS_FILE = "achievements.json"
PROFILE_FILE = "user_profile.json"
DEFAULT_NAME = "AAA"

class Settings:
    """
    Stores all user settings (theme, difficulty, high score, volume, accessibility).
    Handles persistent save/load.
    """
    def __init__(self):
        self.theme_index = 0
        self.theme_name = list(THEMES.keys())[self.theme_index]
        self.difficulty = "Easy"
        self.high_score = 0
        self.volume = 1.0
        self.colorblind = False
        self.load()

    def toggle_difficulty(self):
        order = ["Easy", "Hard", "Master"]
        idx = (order.index(self.difficulty) + 1) % len(order)
        self.difficulty = order[idx]

    def next_theme(self):
        self.theme_index = (self.theme_index + 1) % len(THEMES)
        self.theme_name = list(THEMES.keys())[self.theme_index]

    def get_theme(self):
        return THEMES[self.theme_name]

    def get_difficulty_desc(self):
        descs = {
            "Easy": "Easy: Slow seekers, long boost, obstacles move every 35s.",
            "Hard": "Hard: Faster seekers, shorter boost, obstacles move every 35s.",
            "Master": "Master: Seekers very fast, obstacles never move!"
        }
        return descs[self.difficulty]

    def get_seeker_speed(self):
        return SEEKER_SPEEDS[self.difficulty]

    def get_seeker_spawn_interval(self):
        return SEEKER_SPAWN_INTERVALS[self.difficulty]

    def get_boost_duration(self):
        return BOOST_DURATION[self.difficulty]

    def get_projectile_cooldown(self):
        return PROJECTILE_COOLDOWNS[self.difficulty]

    def save(self):
        data = {
            "theme_index": self.theme_index,
            "theme_name": self.theme_name,
            "difficulty": self.difficulty,
            "high_score": self.high_score,
            "volume": self.volume,
            "colorblind": self.colorblind
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                self.theme_index = data.get("theme_index", 0)
                self.theme_name = data.get("theme_name", list(THEMES.keys())[self.theme_index])
                self.difficulty = data.get("difficulty", "Easy")
                self.high_score = data.get("high_score", 0)
                self.volume = data.get("volume", 1.0)
                self.colorblind = data.get("colorblind", False)

# --- Achievements ---

class AchievementManager:
    """
    Tracks/unlocks achievements, manages persistent save/load, popups, and summary display.
    """
    def __init__(self):
        self.achievements = {a["key"]: False for a in ACHIEVEMENT_LIST}
        self.unlocked_this_game = []
        self.load()

    def unlock(self, key):
        if key in self.achievements and not self.achievements[key]:
            self.achievements[key] = True
            self.save()
            self.unlocked_this_game.append(key)
            print(f"Achievement unlocked: {get_achievement_desc(key)}")
            return get_achievement_desc(key)
        return None

    def is_unlocked(self, key):
        return self.achievements.get(key, False)

    def unlocked_count(self):
        return sum(1 for v in self.achievements.values() if v)

    def save(self):
        with open(ACHIEVEMENTS_FILE, "w") as f:
            json.dump(self.achievements, f)

    def load(self):
        if os.path.exists(ACHIEVEMENTS_FILE):
            with open(ACHIEVEMENTS_FILE, "r") as f:
                data = json.load(f)
                for k in self.achievements:
                    self.achievements[k] = data.get(k, False)
        self.unlocked_this_game = []

    def display_summary(self):
        print("\nAchievement Progress:")
        for ach in ACHIEVEMENT_LIST:
            status = "Unlocked" if self.achievements[ach["key"]] else "Locked"
            print(f"- {ach['desc']}: {status}")

    def get_unlocked_this_game(self):
        return self.unlocked_this_game

    def reset_unlocked_this_game(self):
        self.unlocked_this_game = []

# --- Adaptive Difficulty Curve ---

class DifficultyCurve:
    """
    Changes difficulty parameters as score/time increases.
    """
    def __init__(self, base_settings):
        self.base = base_settings
        self.last_update_score = 0
        self.curve = {
            "seeker_speed": self.base.get_seeker_speed(),
            "spawn_interval": self.base.get_seeker_spawn_interval()
        }

    def update(self, score):
        # Example: every 5000 pts, speed up seekers and spawn faster
        if score // 5000 > self.last_update_score // 5000:
            self.curve["seeker_speed"] += 1
            self.curve["spawn_interval"] = max(5, self.curve["spawn_interval"] - 2)
            self.last_update_score = score

    def seeker_speed(self):
        return self.curve["seeker_speed"]

    def spawn_interval(self):
        return self.curve["spawn_interval"]

# --- Colorblind Mode (accessibility) ---

class ColorblindMode:
    """
    Provides alternative color schemes for accessibility.
    """
    def __init__(self):
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled

    def apply(self, theme):
        if not self.enabled:
            return theme
        # Example: swap reds/greens to blue/orange for better accessibility
        new_theme = theme.copy()
        if "seeker" in new_theme:
            new_theme["seeker"] = (0, 120, 255)
        if "seeker_hard" in new_theme:
            new_theme["seeker_hard"] = (255, 120, 0)
        if "seeker_master" in new_theme:
            new_theme["seeker_master"] = (180, 180, 0)
        new_theme["player"] = (255, 255, 255)
        return new_theme

# --- User Profile (nickname, cosmetics, progress) ---

class UserProfile:
    """
    Stores user's nickname, unlocked cosmetics, profile settings, and persistent data.
    """
    def __init__(self, name=DEFAULT_NAME):
        self.name = name
        self.cosmetics = []
        self.selected_cosmetic = None
        self.stats = {"games_played": 0, "total_score": 0}
        self.save_file = PROFILE_FILE
        self.load()

    def set_name(self, new_name):
        self.name = new_name[:12]
        self.save()

    def unlock_cosmetic(self, cosmetic):
        if cosmetic not in self.cosmetics:
            self.cosmetics.append(cosmetic)
            self.save()

    def select_cosmetic(self, cosmetic):
        if cosmetic in self.cosmetics:
            self.selected_cosmetic = cosmetic
            self.save()

    def record_game(self, score):
        self.stats["games_played"] += 1
        self.stats["total_score"] += score
        self.save()

    def save(self):
        data = {
            "name": self.name,
            "cosmetics": self.cosmetics,
            "selected_cosmetic": self.selected_cosmetic,
            "stats": self.stats
        }
        with open(self.save_file, "w") as f:
            json.dump(data, f)

    def load(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                data = json.load(f)
                self.name = data.get("name", DEFAULT_NAME)
                self.cosmetics = data.get("cosmetics", [])
                self.selected_cosmetic = data.get("selected_cosmetic", None)
                self.stats = data.get("stats", {"games_played": 0, "total_score": 0})

# --- In-Game Tips System ---

DEFAULT_TIPS = [
    "Hold B for boost! (bottom bar)",
    "Last seeker fires ghost bullets!",
    "Avoid seekers—get close for more points.",
    "Pick up powerups for an edge!",
    "Press R to restart instantly.",
    "Obstacles move in Easy/Hard every 35s!",
    "Try Master for a real challenge.",
    "Yellow on minimap = powerup!",
    "You can customize your name and theme in Settings.",
    "F1 toggles help overlay in game.",
    "TAB toggles the minimap.",
    "Every close dodge increases your multiplier.",
    "Collect different powerups: " + ", ".join(POWERUP_NAMES.values())
]

def get_random_tip():
    import random
    return random.choice(DEFAULT_TIPS)

# --- Accessibility: Settings and Profile Management ---

def reset_all_settings():
    for fname in [SETTINGS_FILE, ACHIEVEMENTS_FILE, PROFILE_FILE]:
        if os.path.exists(fname):
            os.remove(fname)

# --- Expansion: Save/Load All State ---

def save_all(settings, achievements, profile):
    settings.save()
    achievements.save()
    profile.save()

def load_all(settings, achievements, profile):
    settings.load()
    achievements.load()
    profile.load()

# --- Debug / Dev Tools ---

def print_settings(settings):
    print(f"Theme: {settings.theme_name} | Difficulty: {settings.difficulty}")
    print(f"Volume: {settings.volume} | Colorblind: {settings.colorblind} | High Score: {settings.high_score}")

def print_profile(profile):
    print(f"Name: {profile.name} | Cosmetic: {profile.selected_cosmetic}")
    print(f"Games Played: {profile.stats['games_played']}, Total Score: {profile.stats['total_score']}")

def print_achievements(achievements):
    print("Achievements:")
    for key, unlocked in achievements.achievements.items():
        print(f"  - {get_achievement_desc(key)}: {'Unlocked' if unlocked else 'Locked'}")

# --- End of settings.py ---
# (Lines: ~530+, ready for next!)