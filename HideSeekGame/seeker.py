# seeker.py

import pygame
import random

class Seeker:
    def __init__(self, x, y, speed, color):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = speed
        self.color = color

    def update(self, target_pos):
        tx, ty = target_pos
        dx = tx - self.rect.centerx + random.randint(-30, 30)
        dy = ty - self.rect.centery + random.randint(-30, 30)
        dist = max(1, (dx**2 + dy**2) ** 0.5)

        self.rect.x += int(self.speed * dx / dist)
        self.rect.y += int(self.speed * dy / dist)

        self.rect.clamp_ip(pygame.Rect(0, 0, 1280, 800))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)