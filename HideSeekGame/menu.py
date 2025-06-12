import pygame
from config import FONT_NAME, WIDTH, HEIGHT

class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = pygame.font.Font(FONT_NAME, 32)

    def draw(self, screen):
        pygame.draw.rect(screen, (70, 70, 70), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        text = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def draw_menu(screen, buttons):
    screen.fill((20, 20, 20))
    for b in buttons:
        b.draw(screen)
    pygame.display.flip()

def draw_settings(screen, settings):
    screen.fill((50, 50, 50))
    font = pygame.font.Font(FONT_NAME, 28)
    desc = settings.get_difficulty_desc()
    texts = [
        f"Settings",
        f"Theme: {settings.theme_name} (Press T)",
        f"Difficulty: {settings.difficulty} (Press D)",
        desc,
        f"High Score: {settings.high_score}",
        "Controls:",
        "WASD / Arrow Keys - Move",
        "B - Boost (cooldown shown on bar)",
        "ESC - Pause",
        "R - Restart instantly",
        "T - Change Theme",
        "D - Toggle Difficulty"
    ]
    for i, line in enumerate(texts):
        txt = font.render(line, True, (255, 255, 255))
        screen.blit(txt, (60, 40 + i * 40))
    pygame.display.flip()

def draw_pause(screen):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(FONT_NAME, 48)
    text = font.render("Paused - Press C to Continue or Q to Quit", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.flip()

def draw_game_over(screen, score, high_score, leaderboard):
    screen.fill((10, 10, 10))
    font = pygame.font.Font(FONT_NAME, 48)
    text = font.render(f"Game Over - Score: {score}", True, (255, 255, 255))
    hi_text = font.render(f"High Score: {high_score}", True, (180, 255, 180))
    instruct = pygame.font.Font(FONT_NAME, 36).render("Press R to Restart or Q to Quit", True, (200, 200, 200))
    screen.blit(text, text.get_rect(center=(WIDTH // 2, 240)))
    screen.blit(hi_text, hi_text.get_rect(center=(WIDTH // 2, 320)))
    screen.blit(instruct, instruct.get_rect(center=(WIDTH // 2, 390)))
    font_small = pygame.font.Font(FONT_NAME, 30)
    lb_title = font_small.render("Leaderboard (Top 5)", True, (255, 255, 0))
    screen.blit(lb_title, (WIDTH // 2 - 90, 440))
    for i, sc in enumerate(leaderboard):
        lb_line = font_small.render(f"{i+1}. {sc}", True, (255, 255, 255))
        screen.blit(lb_line, (WIDTH // 2 - 60, 480 + i * 36))
    pygame.display.flip()

def draw_boost_bar(screen, player):
    w, h = 300, 20
    x, y = WIDTH//2-w//2, HEIGHT-40
    pygame.draw.rect(screen, (80, 80, 80), (x, y, w, h), 0)
    if player.boost_cooldown > 0:
        fill = int(w * (1 - player.boost_cooldown / 1800))
        pygame.draw.rect(screen, (0, 200, 80), (x, y, fill, h), 0)
    elif player.boost_active:
        fill = int(w * (player.boost_timer / player.settings.get_boost_duration()))
        pygame.draw.rect(screen, (0, 255, 255), (x, y, fill, h), 0)
    pygame.draw.rect(screen, (255, 255, 255), (x, y, w, h), 2)