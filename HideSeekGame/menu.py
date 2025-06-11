import pygame
from config import BLACK, WHITE

class Menu:
    def __init__(self):
        self.font = pygame.font.Font(None, 50)
        self.options = ["Play", "Exit"]
        self.selected_index = 0

    def draw(self, screen):
        screen.fill(BLACK)
        for index, option in enumerate(self.options):
            color = WHITE if index == self.selected_index else (180, 180, 180)
            text = self.font.render(option, True, color)
            screen.blit(text, (550, 300 + index * 50))

    def navigate(self, keys):
        if keys[pygame.K_UP] and self.selected_index > 0:
            self.selected_index -= 1
        if keys[pygame.K_DOWN] and self.selected_index < len(self.options) - 1:
            self.selected_index += 1
        return self.options[self.selected_index] if keys[pygame.K_RETURN] else None
