import pygame
import random
from config import SEEKER_SPEED, SEEKER_CHASE_RANGE, WIDTH, HEIGHT, RED

class Seeker:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = SEEKER_SPEED

    def move(self, player):
        """Chase player if close enough, otherwise move randomly."""
        distance_x = abs(self.rect.x - player.rect.x)
        distance_y = abs(self.rect.y - player.rect.y)

        if distance_x < SEEKER_CHASE_RANGE and distance_y < SEEKER_CHASE_RANGE:
            self.rect.x += self.speed if self.rect.x < player.rect.x else -self.speed
            self.rect.y += self.speed if self.rect.y < player.rect.y else -self.speed
        else:
            direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            if direction == "UP": self.rect.y -= self.speed
            elif direction == "DOWN": self.rect.y += self.speed
            elif direction == "LEFT": self.rect.x -= self.speed
            elif direction == "RIGHT": self.rect.x += self.speed

        # Keep seeker inside screen boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
