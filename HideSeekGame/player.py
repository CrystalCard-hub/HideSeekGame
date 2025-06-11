# player.py

import pygame

class Player:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.speed = 5
        self.color = color
        self.boost_active = False
        self.boost_timer = 0
        self.boost_cooldown = 0

    def update(self, keys):
        vel = self.speed * (2 if self.boost_active else 1)
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.rect.y -= vel
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.rect.y += vel
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.rect.x -= vel
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.rect.x += vel

        self.rect.clamp_ip(pygame.Rect(0, 0, 1280, 800))

        if self.boost_active:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.boost_active = False
                self.boost_cooldown = 1800

        elif self.boost_cooldown > 0:
            self.boost_cooldown -= 1

    def try_boost(self):
        if self.boost_cooldown == 0 and not self.boost_active:
            self.boost_active = True
            self.boost_timer = 180

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)