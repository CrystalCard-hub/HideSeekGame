import pygame

class Player:
    def __init__(self, x, y):
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 0, 255))  # Blue color for player
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5

   def move(self, keys):
    velocity = [0, 0]
    if keys[pygame.K_w]: velocity[1] -= self.speed
    if keys[pygame.K_s]: velocity[1] += self.speed
    if keys[pygame.K_a]: velocity[0] -= self.speed
    if keys[pygame.K_d]: velocity[0] += self.speed
    self.rect.x += velocity[0]
    self.rect.y += velocity[1]

    def draw(self, screen):
        screen.blit(self.image, self.rect)
