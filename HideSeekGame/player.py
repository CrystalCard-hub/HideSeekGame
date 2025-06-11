# player.py

import pygame
from config import PLAYER_SPEED, BOOST_SPEED, BOOST_DURATION, BOOST_COOLDOWN

class Player:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.color = color
        self.speed = PLAYER_SPEED
        self.boost_timer = 0
        self.boost_cooldown = 0

    def handle_input(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -1
        if keys[pygame.K_s]: dy = 1
        if keys[pygame.K_a]: dx = -1
        if keys[pygame.K_d]: dx = 1

        if keys[pygame.K_b] and self.boost_cooldown <= 0:
            self.boost_timer = BOOST_DURATION
            self.boost_cooldown = BOOST_COOLDOWN

        speed = BOOST_SPEED if self.boost_timer > 0 else PLAYER_SPEED

        self.rect.x += dx * speed
        self.rect.y += dy * speed

        self.rect.clamp_ip(pygame.Rect(0, 0, 1280, 800))

    def update(self):
        if self.boost_timer > 0:
            self.boost_timer -= 1
        elif self.boost_cooldown > 0:
            self.boost_cooldown -= 1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)