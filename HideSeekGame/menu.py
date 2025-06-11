# menu.py

import pygame
from config import FONT_NAME

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

    texts = [
        f"Settings",
        f"Theme: {settings.theme_name} (Press T)",
        f"Difficulty: {settings.difficulty} (Press D)",
        f"High Score: {settings.high_score}",
        "Controls:",
        "WASD / Arrow Keys - Move",
        "B - Boost (30s cooldown)",
        "ESC - Pause",
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
    screen.blit(text, text.get_rect(center=(640, 400)))
    pygame.display.flip()

def draw_game_over(screen, score):
    screen.fill((10, 10, 10))
    font = pygame.font.Font(FONT_NAME, 48)
    text = font.render(f"Game Over - Score: {score}", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=(640, 400)))
    pygame.display.flip()