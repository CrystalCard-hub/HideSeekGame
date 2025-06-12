# Hide & Seek+ Main Game Loop - 2025 Refined Edition
# Author: CrystalCard-hub & Copilot
# Lines: 500+ (includes docstrings, clean modular structure, polish features)

import pygame
import sys
import random
import math
import time
from config import (
    WIDTH, HEIGHT, FPS, FONT_NAME, SEEKER_SIZE, OBSTACLE_COUNT, OBSTACLE_SIZE, submit_score, read_leaderboard,
    MAX_SEEKERS, PROJECTILE_SIZE, PROJECTILE_SPEED, OBSTACLE_RELOCATE_FRAMES, THEMES, POWERUP_COLORS, POWERUP_NAMES,
    POWERUP_DURATION, lerp, clamp, color_lerp, minimap_coords, get_achievement_desc
)
from settings import Settings, AchievementManager, DifficultyCurve, UserProfile, ColorblindMode, get_random_tip
from player import Player, Powerup
from seeker import Seeker, ParticleManager, GoldenSeeker
from menu import (
    Button, draw_menu, draw_settings, draw_pause, draw_game_over, draw_boost_bar, draw_minimap,
    animate_menu_transition, draw_achievement_popup, draw_help_overlay
)

# --- Utility Functions ---

def get_non_overlapping_spawn(seekers, obstacles, size=SEEKER_SIZE, max_tries=80):
    edges = [
        lambda: (random.randint(0, WIDTH-size), 0),
        lambda: (random.randint(0, WIDTH-size), HEIGHT-size),
        lambda: (0, random.randint(0, HEIGHT-size)),
        lambda: (WIDTH-size, random.randint(0, HEIGHT-size)),
    ]
    for _ in range(max_tries):
        x, y = random.choice(edges)()
        new_rect = pygame.Rect(x, y, size, size)
        collision = any(s.rect.colliderect(new_rect) for s in seekers) or any(ob.colliderect(new_rect) for ob in obstacles)
        if not collision:
            return x, y
    return 0, 0

def random_obstacles(count, size=OBSTACLE_SIZE, objects_to_avoid=None):
    obs = []
    avoid = objects_to_avoid if objects_to_avoid else []
    for _ in range(count):
        tries = 0
        while tries < 50:
            x = random.randint(0, WIDTH-size)
            y = random.randint(0, HEIGHT-size)
            newr = pygame.Rect(x, y, size, size)
            if not any(ob.colliderect(newr) for ob in obs) and not any(a.colliderect(newr) for a in avoid):
                obs.append(newr)
                break
            tries += 1
    return obs

def find_safe_player_spawn(obstacles, size=40, max_tries=100):
    for _ in range(max_tries):
        x = random.randint(0, WIDTH-size)
        y = random.randint(0, HEIGHT-size)
        player_rect = pygame.Rect(x, y, size, size)
        if not any(ob.colliderect(player_rect) for ob in obstacles):
            return x, y
    return WIDTH//2, HEIGHT//2

def in_bounds(rect):
    return 0 <= rect.x < WIDTH and 0 <= rect.y < HEIGHT

def animate_obstacles_move(obstacles, new_positions, progress):
    for ob, (nx, ny) in zip(obstacles, new_positions):
        ox, oy = ob.x, ob.y
        ob.x = int(ox + (nx-ox)*progress)
        ob.y = int(oy + (ny-oy)*progress)

# --- Ghost Projectile Class ---
class Projectile:
    def __init__(self, x, y, dx, dy):
        self.rect = pygame.Rect(x, y, PROJECTILE_SIZE, PROJECTILE_SIZE)
        self.dx = dx
        self.dy = dy
        self.age = 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.age += 1

    def draw(self, screen):
        color = (120, 0, 255) if self.age % 10 < 5 else (0, 255, 255)
        pygame.draw.rect(screen, color, self.rect)

    def is_offscreen(self):
        return not pygame.Rect(0, 0, WIDTH, HEIGHT).colliderect(self.rect)

# --- Main Game Loop ---

def main():
    """
    Entry point for the Hide & Seek+ game.
    Handles menu, settings, and main game loop.
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hide & Seek+")
    clock = pygame.time.Clock()

    font = pygame.font.Font(FONT_NAME, 28)
    settings = Settings()
    achievements = AchievementManager()
    profile = UserProfile()
    colorblind = ColorblindMode()

    # Menu Buttons
    play_btn = Button((WIDTH//2 - 100, 300, 200, 60), "Play")
    settings_btn = Button((WIDTH//2 - 100, 400, 200, 60), "Settings")
    help_btn = Button((WIDTH//2 - 100, 500, 200, 60), "Help")
    exit_btn = Button((WIDTH//2 - 100, 600, 200, 60), "Exit")

    state = "menu"
    tips = [
        "Hold B for boost! (bottom bar)",
        "Last seeker fires ghost bullets!",
        "Avoid seekers—get close for more points.",
        "Pick up powerups for an edge!",
        "Press R to restart instantly.",
        "Obstacles move in Easy/Hard every 35s!",
        "Try Master for a real challenge.",
        "Yellow on minimap = powerup!",
        "Open Settings for colorblind mode."
    ]

    def game_loop():
        theme = settings.get_theme()
        obstacles = []
        # --- Initial spawn: safe
        while True:
            obstacles = random_obstacles(OBSTACLE_COUNT, size=OBSTACLE_SIZE)
            spawn_x, spawn_y = find_safe_player_spawn(obstacles, size=40)
            player_rect = pygame.Rect(spawn_x, spawn_y, 40, 40)
            if not any(ob.colliderect(player_rect) for ob in obstacles):
                break

        player = Player(spawn_x, spawn_y, theme["player"], settings)
        seekers = []
        particle_mgr = ParticleManager()
        seeker_timer = 0
        score = 0
        score_timer = 0
        paused = False
        seeker_spawn_interval = settings.get_seeker_spawn_interval()
        seeker_speed = settings.get_seeker_speed()
        projectiles = []
        projectile_cooldown = 0
        obstacle_relocate_timer = 0
        moving_obstacles = False
        obstacle_move_frames = 45
        obstacle_move_progress = 0
        new_obstacle_positions = []
        powerups = []
        powerup_timer = 0
        screen_shake = 0
        achievement_popup = None
        popup_timer = 0
        last_near_miss = 0
        multiplier = 1
        multiplier_anim = 0
        help_overlay = False
        minimap_toggle = True
        last_mult_popup = 0

        # --- Game Inner Loop ---
        while True:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = True
                    if event.key == pygame.K_b:
                        player.try_boost()
                    if event.key == pygame.K_r:
                        return True  # R to restart
                    if event.key == pygame.K_F1:
                        help_overlay = not help_overlay
                    if event.key == pygame.K_m:  # <--- Changed from TAB to M
                        minimap_toggle = not minimap_toggle

            if paused:
                draw_pause(screen)
                while paused:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_c:
                                paused = False
                            elif event.key == pygame.K_q:
                                return
                    clock.tick(FPS)
                continue

            # ----- Obstacles relocate logic (not in Master) -----
            if settings.difficulty != "Master":
                if not moving_obstacles:
                    obstacle_relocate_timer += 1
                if obstacle_relocate_timer >= OBSTACLE_RELOCATE_FRAMES:
                    moving_obstacles = True
                    new_obstacle_positions = []
                    player_rect = player.rect
                    while True:
                        attempted = random_obstacles(OBSTACLE_COUNT, size=OBSTACLE_SIZE, objects_to_avoid=[player_rect])
                        if not any(ob.colliderect(player_rect) for ob in attempted):
                            break
                    for ob in attempted:
                        new_obstacle_positions.append((ob.x, ob.y))
                    obstacle_move_progress = 0
                    obstacle_relocate_timer = 0
                if moving_obstacles:
                    obstacle_move_progress += 1
                    t = min(obstacle_move_progress / obstacle_move_frames, 1.0)
                    animate_obstacles_move(obstacles, new_obstacle_positions, t)
                    if t >= 1.0:
                        for ob, (nx, ny) in zip(obstacles, new_obstacle_positions):
                            ob.x, ob.y = nx, ny
                        moving_obstacles = False
                        # --- UNSTUCK LOGIC ---
                        # If player is stuck in obstacle, move to nearest free spot
                        if any(ob.colliderect(player.rect) for ob in obstacles):
                            for _ in range(100):
                                x = random.randint(0, WIDTH - player.rect.width)
                                y = random.randint(0, HEIGHT - player.rect.height)
                                test_rect = pygame.Rect(x, y, player.rect.width, player.rect.height)
                                if not any(ob.colliderect(test_rect) for ob in obstacles):
                                    player.rect.x, player.rect.y = x, y
                                    break

            # ----- Powerup spawn and collect logic -----
            powerup_timer += 1
            if powerup_timer > random.randint(700, 1300) and len(powerups) < 2:
                kinds = ["shield", "slow", "multiplier", "heal"]
                kind = random.choice(kinds)
                for _ in range(30):
                    px = random.randint(20, WIDTH-60)
                    py = random.randint(20, HEIGHT-60)
                    prect = pygame.Rect(px, py, 36, 36)
                    if not any(ob.colliderect(prect) for ob in obstacles):
                        powerups.append(Powerup(px, py, kind))
                        break
                powerup_timer = 0

            # --- Player update ---
            player.update(keys, obstacles)
            for i, seeker in enumerate(seekers):
                other_rects = [s.rect for j, s in enumerate(seekers) if j != i]
                seeker.update(player.rect, other_rects, obstacles)
                px, py = player.rect.center
                sx, sy = seeker.rect.center
                if math.hypot(px-sx, py-sy) < 65:
                    if pygame.time.get_ticks() - last_near_miss > 550:
                        multiplier = min(multiplier+1, 5)
                        last_near_miss = pygame.time.get_ticks()
                        multiplier_anim = 18
                        last_mult_popup = pygame.time.get_ticks()

            # --- Projectiles: last seeker fires ghost bullets ---
            if len(seekers) >= MAX_SEEKERS:
                last_seeker = seekers[-1]
                projectile_cooldown += 1
                cooldown = settings.get_projectile_cooldown()
                if projectile_cooldown >= cooldown:
                    dx = player.rect.centerx - last_seeker.rect.centerx
                    dy = player.rect.centery - last_seeker.rect.centery
                    dist = max(1, (dx**2 + dy**2)**0.5)
                    vx = int(PROJECTILE_SPEED * dx / dist)
                    vy = int(PROJECTILE_SPEED * dy / dist)
                    px = last_seeker.rect.centerx - PROJECTILE_SIZE // 2
                    py = last_seeker.rect.centery - PROJECTILE_SIZE // 2
                    projectiles.append(Projectile(px, py, vx, vy))
                    projectile_cooldown = 0

            for proj in projectiles[:]:
                proj.update()
                if proj.is_offscreen():
                    projectiles.remove(proj)
                elif proj.rect.colliderect(player.rect):
                    screen_shake = 24
                    particle_mgr.spawn_impact(player.rect.centerx, player.rect.centery, (255,0,255))
                    achievements.unlock("Ghosted")
                    settings.high_score = max(settings.high_score, score)
                    leaderboard = submit_score(score, profile.name)
                    draw_game_over(screen, score, settings.high_score, leaderboard, achievements)
                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_r:
                                    return True
                                elif event.key == pygame.K_q:
                                    return False
                        clock.tick(FPS)

            # --- Powerup collect ---
            for p in powerups[:]:
                if player.rect.colliderect(p.rect):
                    achievements.unlock("Collector")
                    particle_mgr.spawn_collect(p.rect.centerx, p.rect.centery, p.kind)
                    player.apply_powerup(p.kind)
                    powerups.remove(p)

            seeker_timer += 1
            score_timer += 1

            # --- Adaptive difficulty ---
            if settings.difficulty in ("Hard", "Master") and score // 2000 > 0:
                seeker_spawn_interval = max(7, settings.get_seeker_spawn_interval() - (score // 2000) * 2)
            if settings.difficulty == "Master":
                seeker_speed = settings.get_seeker_speed() + score // 3000
            else:
                seeker_speed = settings.get_seeker_speed()

            if seeker_timer >= FPS * seeker_spawn_interval and len(seekers) < MAX_SEEKERS:
                color_key = "seeker"
                if settings.difficulty == "Hard":
                    color_key = "seeker_hard"
                elif settings.difficulty == "Master":
                    color_key = "seeker_master"
                color = theme[color_key]
                x, y = get_non_overlapping_spawn(seekers, obstacles)
                if random.random() < 0.05 and len(seekers) > 3:
                    seekers.append(GoldenSeeker(x, y, seeker_speed+1, particle_mgr))
                else:
                    seekers.append(Seeker(x, y, color, seeker_speed, particle_mgr))
                seeker_timer = 0

            if score_timer >= FPS:
                score += 143 * multiplier
                score_timer = 0
                if multiplier > 1:
                    multiplier = max(1, multiplier-1)

            # --- Seeker collision/game over ---
            for seeker in seekers:
                if seeker.rect.colliderect(player.rect):
                    screen_shake = 18
                    particle_mgr.spawn_impact(player.rect.centerx, player.rect.centery, (255,0,0))
                    achievements.unlock("Tagged")
                    settings.high_score = max(settings.high_score, score)
                    leaderboard = submit_score(score, profile.name)
                    draw_game_over(screen, score, settings.high_score, leaderboard, achievements)
                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_r:
                                    return True
                                elif event.key == pygame.K_q:
                                    return False
                        clock.tick(FPS)

            # --- Particles, screen shake ---
            particle_mgr.update()
            draw_offset = [0,0]
            if screen_shake > 0:
                draw_offset[0] = random.randint(-screen_shake, screen_shake)
                draw_offset[1] = random.randint(-screen_shake, screen_shake)
                screen_shake = max(0, screen_shake-2)

            # --- Drawing ---
            screen.fill(theme["bg"])
            for ob in obstacles:
                pygame.draw.rect(screen, (70, 70, 90), ob.move(draw_offset))
            for p in powerups:
                p.draw(screen, offset=draw_offset)
            player.draw(screen, offset=draw_offset)
            for seeker in seekers:
                seeker.draw(screen, offset=draw_offset)
            for proj in projectiles:
                proj.draw(screen)

            particle_mgr.draw(screen, offset=draw_offset)
            draw_boost_bar(screen, player)
            if minimap_toggle:
                draw_minimap(screen, player, seekers, obstacles, powerups)
            timer_text = font.render(
                f"Seeker Spawn: {max(0, seeker_spawn_interval - seeker_timer // FPS)} | Seekers: {len(seekers)}/{MAX_SEEKERS}", True, (255, 255, 255)
            )
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            high_score_text = font.render(f"High Score: {settings.high_score}", True, (180, 255, 180))
            if multiplier > 1 or multiplier_anim > 0:
                multiplier_text = font.render(f"Multiplier: x{multiplier}", True, (255, 220, 0))
                screen.blit(multiplier_text, (10, 70+abs(multiplier_anim)))
                if multiplier_anim > 0:
                    multiplier_anim -= 1
            screen.blit(timer_text, (10, 10))
            screen.blit(score_text, (10, 40))
            screen.blit(high_score_text, (10, 100))
            # draw_tips(screen, tips, score)  # <-- Tips removed from gameplay HUD
            if achievement_popup:
                popup_timer += 1
                draw_achievement_popup(screen, achievement_popup)
                if popup_timer > 120:
                    achievement_popup = None
                    popup_timer = 0
            if help_overlay:
                draw_help_overlay(screen)
            pygame.display.flip()
            clock.tick(FPS)

    # --- Main Menu Loop ---
    transition_anim = 0
    while True:
        if state == "menu":
            animate_menu_transition(screen, transition_anim)
            draw_menu(screen, [play_btn, settings_btn, help_btn, exit_btn])
            transition_anim = min(transition_anim + 1, 25)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if play_btn.is_clicked(pos):
                        while True:
                            res = game_loop()
                            if res is True:
                                continue
                            else:
                                break
                    elif settings_btn.is_clicked(pos):
                        state = "settings"
                    elif help_btn.is_clicked(pos):
                        state = "help"
                    elif exit_btn.is_clicked(pos):
                        pygame.quit(); sys.exit()
        elif state == "settings":
            draw_settings(screen, settings)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        settings.next_theme()
                    elif event.key == pygame.K_d:
                        settings.toggle_difficulty()
                    elif event.key == pygame.K_c:
                        colorblind.toggle()
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
            clock.tick(FPS)
        elif state == "help":
            draw_help_overlay(screen, main_menu=True)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
            clock.tick(FPS)

if __name__ == "__main__":
    main()

# --- End of main.py ---