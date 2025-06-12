import pygame
from config import PLAYER_SIZE, PLAYER_SPEED, WIDTH, HEIGHT

class Player:
    def __init__(self, x, y, color, settings):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.color = color
        self.boost_active = False
        self.boost_timer = 0
        self.boost_cooldown = 0
        self.settings = settings

    def update(self, keys, obstacles):
        vel = self.speed * (2 if self.boost_active else 1)
        move_x = move_y = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_y -= vel
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_y += vel
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_x -= vel
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_x += vel

        old_rect = self.rect.copy()
        self.rect.x += move_x
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        for ob in obstacles:
            if self.rect.colliderect(ob):
                self.rect.x = old_rect.x

        old_rect = self.rect.copy()
        self.rect.y += move_y
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        for ob in obstacles:
            if self.rect.colliderect(ob):
                self.rect.y = old_rect.y

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
            self.boost_timer = self.settings.get_boost_duration()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)