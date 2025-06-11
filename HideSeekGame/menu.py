import pygame

class Menu:
    def __init__(self):
        self.font = pygame.font.Font(None, 40)
        self.options = ["Play", "Settings", "Exit"]
        self.selected_index = 0

    def draw(self, screen):
        screen.fill((30, 30, 30))
        for index, option in enumerate(self.options):
            color = (255, 255, 255) if index == self.selected_index else (180, 180, 180)
            text = self.font.render(option, True, color)
            screen.blit(text, (350, 200 + index * 50))

    def navigate(self, keys):
        if keys[pygame.K_UP] and self.selected_index > 0:
            self.selected_index -= 1
        if keys[pygame.K_DOWN] and self.selected_index < len(self.options) - 1:
            self.selected_index += 1
