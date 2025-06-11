# menu.py

import pygame
import sys
from config import FONT_NAME
from settings import GameSettings

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.settings = GameSettings()
        self.font = pygame.font.Font(FONT_NAME, 50)
        self.button_font = pygame.font.Font(FONT_NAME, 30)
        self.buttons = {
            "play": pygame.Rect(500, 300, 280, 50),
            "settings": pygame.Rect(500, 375, 280, 50),
            "exit": pygame.Rect(500, 450, 280, 50)
        }

    def draw(self):
        self.screen.fill(self.settings.theme['bg'])
        title = self.font.render("Hide and Seek", True, (255, 255, 255))
        self.screen.blit(title, (400, 100))

        for key, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (255, 255, 255), rect)
            label = self.button_font.render(key.capitalize(), True, (0, 0, 0))
            self.screen.blit(label, (rect.x + 90, rect.y + 10))

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for key, rect in self.buttons.items():
                    if rect.collidepoint(pos):
                        return key

    def show_settings(self):
        running = True
        while running:
            self.screen.fill((50, 50, 100))  # settings visual cue

            title = self.font.render("Settings", True, (255, 255, 255))
            self.screen.blit(title, (500, 100))

            theme = self.button_font.render(f"Theme: {self.settings.theme_name}", True, (255, 255, 255))
            diff = self.button_font.render(f"Difficulty: {self.settings.difficulty}", True, (255, 255, 255))
            back = self.button_font.render("Press ESC to go back", True, (255, 255, 255))

            self.screen.blit(theme, (480, 250))
            self.screen.blit(diff, (480, 300))
            self.screen.blit(back, (460, 400))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.settings.previous_theme()
                    elif event.key == pygame.K_RIGHT:
                        self.settings.next_theme()
                    elif event.key == pygame.K_UP:
                        self.settings.toggle_difficulty()
                    elif event.key == pygame.K_ESCAPE:
                        running = False