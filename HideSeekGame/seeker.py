import pygame
import random
from config import SEEKER_SIZE, WIDTH, HEIGHT

class Seeker:
    def __init__(self, x, y, color, speed):
        self.rect = pygame.Rect(x, y, SEEKER_SIZE, SEEKER_SIZE)
        self.base_color = color
        self.color = color
        self.speed = speed

        # Stuck detection
        self.last_positions = []
        self.stuck_timer = 0
        self.UNSTUCK_TIME = 600  # 10 seconds at 60fps

    def update(self, player_rect, other_seekers, obstacles, danger_distance=120):
        if len(self.last_positions) > 40:
            self.last_positions.pop(0)
        self.last_positions.append(self.rect.topleft)

        stuck = False
        if len(self.last_positions) == 40:
            moved = max(abs(self.rect.x - self.last_positions[0][0]), abs(self.rect.y - self.last_positions[0][1]))
            if moved < 2:
                self.stuck_timer += 1
                if self.stuck_timer > self.UNSTUCK_TIME:
                    stuck = True
            else:
                self.stuck_timer = 0

        if stuck:
            self.rect.topleft = random.choice([
                (random.randint(0, WIDTH-SEEKER_SIZE), 0),
                (random.randint(0, WIDTH-SEEKER_SIZE), HEIGHT-SEEKER_SIZE),
                (0, random.randint(0, HEIGHT-SEEKER_SIZE)),
                (WIDTH-SEEKER_SIZE, random.randint(0, HEIGHT-SEEKER_SIZE))
            ])
            self.stuck_timer = 0
            self.last_positions.clear()
            self.color = (0, 255, 255)
            return

        dx = player_rect.centerx - self.rect.centerx + random.randint(-30, 30)
        dy = player_rect.centery - self.rect.centery + random.randint(-30, 30)
        distance = max(1, (dx**2 + dy**2)**0.5)
        new_rect = self.rect.copy()
        new_rect.x += int(self.speed * dx / distance)
        new_rect.y += int(self.speed * dy / distance)
        new_rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        blocked = False
        for other in other_seekers:
            if new_rect.colliderect(other):
                blocked = True
        for ob in obstacles:
            if new_rect.colliderect(ob):
                blocked = True
        if not blocked:
            self.rect = new_rect

        px, py = player_rect.center
        sx, sy = self.rect.center
        dist2 = (px - sx)**2 + (py - sy)**2
        if dist2 < danger_distance ** 2:
            self.color = (255, 64, 64)
        elif self.rect.colliderect(player_rect):
            self.color = (255, 255, 255)
        else:
            self.color = self.base_color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)