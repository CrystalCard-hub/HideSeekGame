import pygame
import random
from config import SEEKER_SPEED, WIDTH, HEIGHT, RED

class Seeker:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = SEEKER_SPEED

    def move(self, player):
        """Improved AI: Predict movement and cut player off."""
        if abs(self.rect.x - player.rect.x) < abs(self.rect.y - player.rect.y):
            self.rect.y += self.speed if self.rect.y < player.rect.y else -self.speed
        else:
            self.rect.x += self.speed if self.rect.x < player.rect.x else -self.speed

        # Add unpredictability
        if random.randint(0, 4) == 0:
            self.rect.x += random.choice([-10, 10])
        if random.randint(0, 4) == 1:
            self.rect.y += random.choice([-10, 10])

        # Keep seeker inside screen boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
