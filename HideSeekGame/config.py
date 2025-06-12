import os

WIDTH = 1280
HEIGHT = 800
FPS = 60
FONT_NAME = "freesansbold.ttf"

PLAYER_SIZE = 40
SEEKER_SIZE = 40
PLAYER_SPEED = 5

BOOST_DURATION = {
    "Easy": 180,
    "Hard": 120,
    "Master": 60
}
BOOST_COOLDOWN = 1800

SEEKER_SPEEDS = {
    "Easy": 2,
    "Hard": 4,
    "Master": 7
}
SEEKER_SPAWN_INTERVALS = {
    "Easy": 30,
    "Hard": 20,
    "Master": 10
}

PROJECTILE_COOLDOWNS = {
    "Easy": 240,     # 4 sec
    "Hard": 150,     # 2.5 sec
    "Master": 90     # 1.5 sec
}

MAX_SEEKERS = 10
OBSTACLE_COUNT = 8
OBSTACLE_SIZE = 80

OBSTACLE_RELOCATE_FRAMES = 2100  # 35s at 60 FPS

THEMES = {
    "Dark":   {"bg": (30, 30, 30), "player": (255, 255, 255), "seeker": (255, 0, 0),   "seeker_hard": (0, 0, 255),   "seeker_master": (255, 128, 0)},
    "Light":  {"bg": (240, 240, 240), "player": (50, 50, 50), "seeker": (200, 0, 0),   "seeker_hard": (0, 0, 180),   "seeker_master": (255, 128, 0)},
    "Red":    {"bg": (100, 0, 0), "player": (255, 255, 255), "seeker": (255, 255, 0), "seeker_hard": (0, 255, 255), "seeker_master": (255, 128, 0)}
}

LEADERBOARD_FILE = "leaderboard.txt"

PROJECTILE_SIZE = 18
PROJECTILE_SPEED = 13  # px per frame

def ensure_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "w") as f:
            for _ in range(5):
                f.write("0\n")

def read_leaderboard():
    with open(LEADERBOARD_FILE, "r") as f:
        return [int(x.strip()) for x in f.readlines()]

def submit_score(score):
    scores = read_leaderboard()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:5]
    with open(LEADERBOARD_FILE, "w") as f:
        for s in scores:
            f.write(f"{s}\n")
    return scores

ensure_leaderboard()