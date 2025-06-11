# seeker.py

import pygame
import random

class Seeker:
    def __init__(self, x, y, color, speed):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.color = color
        self.speed = speed

    def update(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx + random.randint(-30, 30)
        dy = player_rect.centery - self.rect.centery + random.randint(-30, 30)
        distance = max(1, (dx**2 + dy**2)**0.5)
        self.rect.x += int(self.speed * dx / distance)
        self.rect.y += int(self.speed * dy / distance)
        self.rect.clamp_ip(pygame.Rect(0, 0, 1280, 800))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)