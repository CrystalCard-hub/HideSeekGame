import pygame
import sys
import random
from config import (
    WIDTH, HEIGHT, FPS, FONT_NAME, SEEKER_SIZE, OBSTACLE_COUNT, OBSTACLE_SIZE, submit_score, read_leaderboard, MAX_SEEKERS,
    PROJECTILE_SIZE, PROJECTILE_SPEED, OBSTACLE_RELOCATE_FRAMES
)
from settings import Settings
from player import Player
from seeker import Seeker
from menu import Button, draw_menu, draw_settings, draw_pause, draw_game_over, draw_boost_bar

class Projectile:
    def __init__(self, x, y, dx, dy):
        self.rect = pygame.Rect(x, y, PROJECTILE_SIZE, PROJECTILE_SIZE)
        self.dx = dx
        self.dy = dy

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, screen):
        pygame.draw.rect(screen, (120, 0, 255), self.rect)

    def is_offscreen(self):
        return not pygame.Rect(0, 0, WIDTH, HEIGHT).colliderect(self.rect)

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hide & Seek")
    clock = pygame.time.Clock()
    font = pygame.font.Font(FONT_NAME, 28)
    settings = Settings()
    play_btn = Button((WIDTH//2 - 100, 300, 200, 60), "Play")
    settings_btn = Button((WIDTH//2 - 100, 400, 200, 60), "Settings")
    exit_btn = Button((WIDTH//2 - 100, 500, 200, 60), "Exit")
    state = "menu"

    def game_loop():
        theme = settings.get_theme()
        # Initial obstacles and safe player spawn
        obstacles = []
        spawn_x = spawn_y = 0
        while True:
            obstacles = random_obstacles(OBSTACLE_COUNT, size=OBSTACLE_SIZE)
            spawn_x, spawn_y = find_safe_player_spawn(obstacles, size=40)
            player_rect = pygame.Rect(spawn_x, spawn_y, 40, 40)
            # Ensure obstacles don't overlap spawn
            if not any(ob.colliderect(player_rect) for ob in obstacles):
                break
        player = Player(spawn_x, spawn_y, theme["player"], settings)
        seekers = []
        seeker_timer = 0
        score = 0
        score_timer = 0
        paused = False
        seeker_spawn_interval = settings.get_seeker_spawn_interval()
        seeker_speed = settings.get_seeker_speed()
        projectiles = []
        projectile_cooldown = 0
        obstacle_relocate_timer = 0

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

            # Obstacle relocate logic (not in Master mode)
            if settings.difficulty != "Master":
                obstacle_relocate_timer += 1
                if obstacle_relocate_timer >= OBSTACLE_RELOCATE_FRAMES:
                    # Relocate obstacles, making sure none overlap player or other obstacles
                    player_rect = player.rect
                    obstacles = random_obstacles(OBSTACLE_COUNT, size=OBSTACLE_SIZE, objects_to_avoid=[player_rect])
                    obstacle_relocate_timer = 0

            player.update(keys, obstacles)
            for i, seeker in enumerate(seekers):
                other_rects = [s.rect for j, s in enumerate(seekers) if j != i]
                seeker.update(player.rect, other_rects, obstacles)

            # Projectiles (last seeker in any mode)
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
                    settings.high_score = max(settings.high_score, score)
                    leaderboard = submit_score(score)
                    draw_game_over(screen, score, settings.high_score, leaderboard)
                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_r:
                                    return True
                                elif event.key == pygame.K_q:
                                    return False
                        clock.tick(FPS)

            seeker_timer += 1
            score_timer += 1
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
                seekers.append(Seeker(x, y, color, seeker_speed))
                seeker_timer = 0

            if score_timer >= FPS:
                score += 143
                score_timer = 0

            for seeker in seekers:
                if seeker.rect.colliderect(player.rect):
                    settings.high_score = max(settings.high_score, score)
                    leaderboard = submit_score(score)
                    draw_game_over(screen, score, settings.high_score, leaderboard)
                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_r:
                                    return True
                                elif event.key == pygame.K_q:
                                    return False
                        clock.tick(FPS)

            screen.fill(theme["bg"])
            for ob in obstacles:
                pygame.draw.rect(screen, (80, 80, 80), ob)
            player.draw(screen)
            for seeker in seekers:
                seeker.draw(screen)
            for proj in projectiles:
                proj.draw(screen)

            timer_text = font.render(
                f"Seeker Spawn: {max(0, seeker_spawn_interval - seeker_timer // FPS)} | Seekers: {len(seekers)}/{MAX_SEEKERS}", True, (255, 255, 255)
            )
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            high_score_text = font.render(f"High Score: {settings.high_score}", True, (180, 255, 180))
            screen.blit(timer_text, (10, 10))
            screen.blit(score_text, (10, 40))
            screen.blit(high_score_text, (10, 70))
            draw_boost_bar(screen, player)
            pygame.display.flip()
            clock.tick(FPS)

    while True:
        if state == "menu":
            draw_menu(screen, [play_btn, settings_btn, exit_btn])
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if play_btn.is_clicked(pos):
                        while True:
                            res = game_loop()
                            if res is True:
                                continue  # restart game immediately!
                            else:
                                break     # return to menu
                    elif settings_btn.is_clicked(pos):
                        state = "settings"
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
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
            clock.tick(FPS)

if __name__ == "__main__":
    main()