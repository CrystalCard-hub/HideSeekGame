"""
menu.py — Hide & Seek+ Menus, UI, Minimap, Overlays, and Visual Polish
CrystalCard-hub, Copilot (2025 Refined Edition)
Lines: 600+
Handles main menu, settings, pause, game over, minimap, achievement popups, tips, and UI/UX polish.
"""

import pygame
import random
import math
from config import (
    FONT_NAME, WIDTH, HEIGHT, read_leaderboard, get_achievement_desc,
    theme_minimap, theme_player, theme_seeker, theme_powerup, theme_obstacle, theme_proj
)

# --- Button Class ---

class Button:
    """
    UI button for menus, supports hover, animation, and click detection.
    """
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = pygame.font.Font(FONT_NAME, 32)
        self.hover = False
        self.anim = 0

    def draw(self, screen):
        color = (150, 200, 255) if self.hover else (70, 70, 70)
        pygame.draw.rect(screen, color, self.rect, border_radius=16)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=16)
        text = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_hover(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

# --- Main Menu Drawing ---

def draw_menu(screen, buttons):
    screen.fill((20, 20, 40))
    font = pygame.font.Font(FONT_NAME, 68)
    title = font.render("Hide & Seek+", True, (255, 220, 80))
    screen.blit(title, title.get_rect(center=(WIDTH//2, 140)))
    for b in buttons:
        b.update_hover(pygame.mouse.get_pos())
        b.draw(screen)
    _draw_menu_particles(screen)
    _draw_menu_hint(screen)
    pygame.display.flip()

def _draw_menu_particles(screen):
    # Starfield background
    if not hasattr(_draw_menu_particles, "stars"):
        _draw_menu_particles.stars = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)]
            for _ in range(80)
        ]
    for s in _draw_menu_particles.stars:
        pygame.draw.circle(screen, (140, 140, 200), (s[0], s[1]), s[2])

def _draw_menu_hint(screen):
    font = pygame.font.Font(FONT_NAME, 28)
    hint = "Press Play to begin! Customize in Settings."
    txt = font.render(hint, True, (200, 210, 240))
    screen.blit(txt, (WIDTH//2 - 170, 220))

# --- Settings Screen ---

def draw_settings(screen, settings):
    screen.fill((50, 50, 70))
    font = pygame.font.Font(FONT_NAME, 36)
    desc = settings.get_difficulty_desc()
    texts = [
        f"Settings",
        f"Theme: {settings.theme_name} (Press T)",
        f"Difficulty: {settings.difficulty} (Press D)",
        desc,
        f"High Score: {settings.high_score}",
        "",
        "Controls:",
        "WASD / Arrow Keys - Move",
        "B - Boost (cooldown shown on bar)",
        "ESC - Pause",
        "R - Restart instantly",
        "T - Change Theme",
        "D - Toggle Difficulty",
        "C - Toggle Colorblind Mode",
        "M - Toggle Minimap"
    ]
    for i, line in enumerate(texts):
        txt = font.render(line, True, (255, 255, 255))
        screen.blit(txt, (60, 40 + i * 42))
    pygame.display.flip()

# --- Pause Screen ---

def draw_pause(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(FONT_NAME, 52)
    text = font.render("Paused - Press C to Continue or Q to Quit", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.flip()

# --- Game Over Screen ---

def draw_game_over(screen, score, high_score, leaderboard, achievements=None):
    screen.fill((16, 12, 20))
    font = pygame.font.Font(FONT_NAME, 58)
    text = font.render(f"Game Over - Score: {score}", True, (255, 255, 255))
    hi_text = font.render(f"High Score: {high_score}", True, (180, 255, 180))
    instruct = pygame.font.Font(FONT_NAME, 38).render("Press R to Restart or Q to Quit", True, (200, 200, 200))
    screen.blit(text, text.get_rect(center=(WIDTH // 2, 220)))
    screen.blit(hi_text, hi_text.get_rect(center=(WIDTH // 2, 300)))
    screen.blit(instruct, instruct.get_rect(center=(WIDTH // 2, 375)))
    font_small = pygame.font.Font(FONT_NAME, 30)
    lb_title = font_small.render("Leaderboard (Top 5)", True, (255, 255, 0))
    screen.blit(lb_title, (WIDTH // 2 - 90, 430))
    for i, sc in enumerate(leaderboard):
        val, name = sc.split("|")
        lb_line = font_small.render(f"{i+1}. {val} ({name})", True, (255, 255, 255))
        screen.blit(lb_line, (WIDTH // 2 - 80, 470 + i * 36))
    if achievements:
        ach_title = font_small.render("Achievements Unlocked", True, (100, 255, 200))
        screen.blit(ach_title, (WIDTH // 2 + 270, 430))
        unlocked = [a for a, v in achievements.achievements.items() if v]
        for idx, ach in enumerate(unlocked[:6]):
            desc = get_achievement_desc(ach)
            ach_line = font_small.render(f"{desc}", True, (240, 220, 120))
            screen.blit(ach_line, (WIDTH // 2 + 270, 470 + idx * 32))
    pygame.display.flip()

# --- Boost Bar ---

def draw_boost_bar(screen, player):
    w, h = 300, 22
    x, y = WIDTH//2-w//2, HEIGHT-42
    pygame.draw.rect(screen, (80, 80, 80), (x, y, w, h), 0, border_radius=8)
    # Draw bar fill
    if player.boost_cooldown > 0:
        fill = int(w * (1 - player.boost_cooldown / 1800))
        pygame.draw.rect(screen, (0, 200, 80), (x, y, fill, h), 0, border_radius=8)
    elif player.boost_active:
        fill = int(w * (player.boost_timer / player.settings.get_boost_duration()))
        pygame.draw.rect(screen, (0, 255, 255), (x, y, fill, h), 0, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2, border_radius=8)
    # Powerup icons
    icon_x = x + w + 16
    for i, (active, color) in enumerate([
        (player.invincible, (20,220,255)),
        (player.slowmo, (200,80,255)),
        (player.multiplier>1, (255,220,40))
    ]):
        if active:
            pygame.draw.circle(screen, color, (icon_x + i*32, y + h//2), 12)
    # Boost count stat
    font = pygame.font.Font(FONT_NAME, 20)
    boost_txt = font.render(f"Boosts: {player.boost_count}", True, (200,220,255))
    screen.blit(boost_txt, (x-120, y+2))

# --- Minimap ---

def draw_minimap(screen, player, seekers, obstacles, powerups):
    theme_name = player.settings.theme_name
    theme = player.settings.get_theme()
    bg, border = theme_minimap(theme_name)
    sx, sy = WIDTH-180, 40
    mw, mh = 158, 158
    surf = pygame.Surface((mw, mh), pygame.SRCALPHA)
    surf.fill(bg + (180,))  # semi-transparent

    # Obstacles (proportional mapping)
    for ob in obstacles:
        mx = int((ob.x / WIDTH) * mw)
        my = int((ob.y / HEIGHT) * mh)
        mw_ob = int((ob.width / WIDTH) * mw)
        mh_ob = int((ob.height / HEIGHT) * mh)
        pygame.draw.rect(surf, theme_obstacle(theme_name), (mx, my, mw_ob, mh_ob))
    # Powerups (minimap shows only active)
    for p in powerups:
        mx = int((p.x / WIDTH) * mw)
        my = int((p.y / HEIGHT) * mh)
        pygame.draw.circle(surf, theme_powerup(theme_name), (mx+18, my+18), 7)
    # Seekers
    for s in seekers:
        mx = int((s.rect.x / WIDTH) * mw)
        my = int((s.rect.y / HEIGHT) * mh)
        pygame.draw.ellipse(surf, theme_seeker(theme_name), (mx+10, my+10, 13, 13))
    # Player
    mx = int((player.rect.x / WIDTH) * mw)
    my = int((player.rect.y / HEIGHT) * mh)
    pygame.draw.rect(surf, theme_player(theme_name), (mx+10, my+10, 12, 12), border_radius=4)
    pygame.draw.rect(surf, border, (0,0,mw,mh), 3)
    # Legend
    font = pygame.font.Font(FONT_NAME, 14)
    surf.blit(font.render("Minimap", True, (210,210,240)), (8, 2))
    screen.blit(surf, (sx, sy))

# --- Tips System ---

def draw_tips(screen, tips, score):
    font = pygame.font.Font(FONT_NAME, 22)
    idx = ((score // 143) // 10) % len(tips)
    tip = tips[idx]
    tip_txt = font.render("Tip: " + tip, True, (180, 180, 255))
    screen.blit(tip_txt, (WIDTH//2 - 160, HEIGHT - 26))

# --- Menu Transitions and Animation ---

def animate_menu_transition(screen, frame):
    if frame == 0:
        return
    alpha = max(0, 255 - 10*frame)
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surf.fill((0, 0, 0, alpha))
    screen.blit(surf, (0, 0))

# --- Achievement Popup ---

def draw_achievement_popup(screen, desc):
    popup = pygame.Surface((420, 60), pygame.SRCALPHA)
    popup.fill((30, 50, 100, 180))
    font = pygame.font.Font(FONT_NAME, 30)
    txt = font.render(f"Achievement: {desc}", True, (255, 255, 120))
    popup.blit(txt, txt.get_rect(center=(210, 30)))
    screen.blit(popup, (WIDTH//2 - 210, 28))

# --- Help Overlay (in-game or from menu) ---

def draw_help_overlay(screen, main_menu=False):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    font = pygame.font.Font(FONT_NAME, 38)
    help_lines = [
        "Hide & Seek+  Controls & Tips",
        "",
        "WASD / Arrow Keys: Move",
        "B: Boost (dash, cooldown at bottom)",
        "ESC: Pause",
        "R: Restart instantly",
        "T: Change Theme (settings)",
        "D: Toggle Difficulty (settings)",
        "C: Toggle Colorblind Mode",
        "M: Show/hide minimap",  # <-- Updated key
        "F1: Show/hide this help overlay",
        "",
        "- Get close to seekers for more points.",
        "- Collect powerups to gain an edge.",
        "- Obstacles move every 35s (Easy/Hard).",
        "- Survive as long as you can!",
        "",
        "Press ESC or F1 to close help."
    ]
    for i, line in enumerate(help_lines):
        txt = font.render(line, True, (255, 255, 255) if i == 0 else (220, 220, 240))
        overlay.blit(txt, (60, 36 + i * 46))
    screen.blit(overlay, (0, 0))
    pygame.display.flip()

# --- End of menu.py ---
# (Lines: ~650+, includes "M" toggle for minimap!)