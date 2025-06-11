import pygame
from config import BACKGROUND_COLOR, WHITE

class Settings:
    def __init__(self):
        self.font = pygame.font.Font(None, 50)
        self.options = ["Difficulty: Normal", "Seeker Speed: 3", "Back"]
        self.selected_index = 0

    def draw(self, screen):
        screen.fill(BACKGROUND_COLOR)
        for index, option in enumerate(self.options):
            color = WHITE if index == self.selected_index else (180, 180, 180)
            text = self.font.render(option, True, color)
            screen.blit(text, (450, 300 + index * 50))

    def navigate(self, key):
        if key == pygame.K_UP and self.selected_index > 0:
            self.selected_index -= 1
        elif key == pygame.K_DOWN and self.selected_index < len(self.options) - 1:
            self.selected_index += 1
        elif key == pygame.K_RETURN:
            return self.options[self.selected_index]  # Return selected option
        return None
