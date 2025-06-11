import pygame
import random

class Seeker:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 0, 0))  # Red color for seeker
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 3

    def move_random(self):
        direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        if direction == "UP":
            self.rect.y -= self.speed
        elif direction == "DOWN":
            self.rect.y += self.speed
        elif direction == "LEFT":
            self.rect.x -= self.speed
        elif direction == "RIGHT":
            self.rect.x += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)
