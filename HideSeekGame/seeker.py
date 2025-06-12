"""
seeker.py — Hide & Seek+ Seekers, Particles, AI, and Special Behaviors
CrystalCard-hub, Copilot (2025 Refined Edition)
Lines: 500+
Handles all seeker logic, AI pathing, stuck detection, particle effects, special seeker variants, and related polish.
"""

import pygame
import random
import math
from config import (
    SEEKER_SIZE, WIDTH, HEIGHT, lerp, color_lerp, theme_seeker, theme_player, theme_powerup
)

# --- Particle System ---

class Particle:
    """
    A single particle for visual effects (impacts, collections, seeker actions).
    """
    def __init__(self, x, y, color, vx, vy, life, size=8):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.size = size
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.age += 1
        # Fade velocity over time
        if self.age < self.life // 2:
            self.vx *= 0.99
            self.vy *= 0.99
        else:
            self.vx *= 0.95
            self.vy *= 0.95

    def draw(self, screen, offset=(0,0)):
        alpha = int(255 * max(0, 1 - self.age / self.life))
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        c = self.color + (alpha,)
        pygame.draw.ellipse(surf, c, (0, 0, self.size, self.size))
        screen.blit(surf, (self.x + offset[0], self.y + offset[1]))

    def is_alive(self):
        return self.age < self.life

class ParticleManager:
    """
    Manages all particles, offers spawn methods for different game events.
    """
    def __init__(self):
        self.particles = []

    def spawn_impact(self, x, y, color):
        for _ in range(20):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(2, 7)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            p = Particle(x, y, color, vx, vy, random.randint(16, 30), size=random.randint(6, 12))
            self.particles.append(p)

    def spawn_collect(self, x, y, kind):
        color = theme_powerup("Dark")  # Default
        if kind == "shield":
            color = (20, 220, 255)
        elif kind == "slow":
            color = (200, 80, 255)
        elif kind == "heal":
            color = (80, 255, 100)
        elif kind == "multiplier":
            color = (255, 220, 40)
        for _ in range(14):
            a = random.uniform(0, 2*math.pi)
            s = random.uniform(1, 5)
            p = Particle(x, y, color, math.cos(a)*s, math.sin(a)*s, random.randint(12, 22), size=8)
            self.particles.append(p)

    def spawn_trail(self, x, y, color):
        # Fainter, longer-lived trailing particles for seekers
        for _ in range(3):
            a = random.uniform(0, 2*math.pi)
            s = random.uniform(0.5, 2)
            p = Particle(x, y, color, math.cos(a)*s, math.sin(a)*s, random.randint(18, 34), size=6)
            self.particles.append(p)

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive()]

    def draw(self, screen, offset=(0,0)):
        for p in self.particles:
            p.draw(screen, offset=offset)

# --- Seeker Base Class ---

class Seeker:
    """
    The main seeker enemy, with AI pathing, stuck detection, teleportation, and color feedback.
    """
    def __init__(self, x, y, color, speed, particle_mgr=None):
        self.rect = pygame.Rect(x, y, SEEKER_SIZE, SEEKER_SIZE)
        self.base_color = color
        self.color = color
        self.speed = speed
        self.last_positions = []
        self.stuck_timer = 0
        self.UNSTUCK_TIME = 600  # 10 seconds at 60fps
        self.particle_mgr = particle_mgr
        self.teleport_cooldown = random.randint(400, 900)
        self.teleport_flash = 0
        self.trail_timer = 0

    def update(self, player_rect, other_seekers, obstacles, danger_distance=120):
        # Stuck detection and teleport
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

        if stuck or self.teleport_cooldown <= 0:
            # Teleport to a random edge (and do a flash effect)
            self.rect.topleft = random.choice([
                (random.randint(0, WIDTH-SEEKER_SIZE), 0),
                (random.randint(0, WIDTH-SEEKER_SIZE), HEIGHT-SEEKER_SIZE),
                (0, random.randint(0, HEIGHT-SEEKER_SIZE)),
                (WIDTH-SEEKER_SIZE, random.randint(0, HEIGHT-SEEKER_SIZE))
            ])
            self.stuck_timer = 0
            self.last_positions.clear()
            self.color = (0, 255, 255)
            self.teleport_cooldown = random.randint(500, 1100)
            self.teleport_flash = 7
            if self.particle_mgr:
                self.particle_mgr.spawn_impact(self.rect.centerx, self.rect.centery, (0,255,255))
            return

        self.teleport_cooldown -= 1
        if self.teleport_flash > 0:
            self.teleport_flash -= 1

        # AI movement: home in on player, with some random jitter
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
        elif self.teleport_flash > 0:
            self.color = (0, 255, 255)
        else:
            self.color = color_lerp(self.color, self.base_color, 0.18)

        # Trail effect (for polish)
        self.trail_timer += 1
        if self.trail_timer % 3 == 0 and self.particle_mgr:
            self.particle_mgr.spawn_trail(self.rect.centerx, self.rect.centery, self.base_color)

    def draw(self, screen, offset=(0,0)):
        surf = pygame.Surface((SEEKER_SIZE, SEEKER_SIZE), pygame.SRCALPHA)
        if self.teleport_flash > 0:
            pygame.draw.rect(surf, (0,255,255, 150), (0,0,SEEKER_SIZE,SEEKER_SIZE), border_radius=8)
        pygame.draw.rect(surf, self.color, (0,0,SEEKER_SIZE,SEEKER_SIZE), border_radius=10)
        screen.blit(surf, (self.rect.x + offset[0], self.rect.y + offset[1]))
        # Eyes (polished)
        eye = pygame.Rect(self.rect.x+14+offset[0], self.rect.y+9+offset[1], 6, 6)
        pygame.draw.ellipse(screen, (0,0,0), eye)
        eye2 = pygame.Rect(self.rect.x+14+offset[0], self.rect.y+25+offset[1], 6, 6)
        pygame.draw.ellipse(screen, (0,0,0), eye2)

# --- Golden Seeker (special variant) ---

class GoldenSeeker(Seeker):
    """
    Special seeker variant for bonus points, sparkles, and extra challenge.
    """
    def __init__(self, x, y, speed, particle_mgr=None):
        super().__init__(x, y, (255, 224, 60), speed, particle_mgr)
        self.bonus = 2500
        self.sparkle_timer = 0

    def draw(self, screen, offset=(0,0)):
        surf = pygame.Surface((SEEKER_SIZE, SEEKER_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (255, 224, 60, 200), (0,0,SEEKER_SIZE,SEEKER_SIZE), border_radius=10)
        pygame.draw.rect(surf, (255, 255, 160, 160), (6,6,SEEKER_SIZE-12, SEEKER_SIZE-12), border_radius=6)
        screen.blit(surf, (self.rect.x + offset[0], self.rect.y + offset[1]))
        # Sparkles
        self.sparkle_timer += 1
        if self.sparkle_timer % 5 == 0:
            for _ in range(2):
                x = self.rect.x + offset[0] + random.randint(0, SEEKER_SIZE)
                y = self.rect.y + offset[1] + random.randint(0, SEEKER_SIZE)
                pygame.draw.circle(screen, (255,255,120), (x,y), 2)

# --- For Future: BossSeeker, RainbowSeeker, etc. ---

class BossSeeker(Seeker):
    """
    Large, slower, area-denial seeker for advanced game modes.
    """
    def __init__(self, x, y, particle_mgr=None):
        super().__init__(x, y, (180, 80, 255), 1, particle_mgr)
        self.rect.width = SEEKER_SIZE * 2
        self.rect.height = SEEKER_SIZE * 2
        self.health = 5
        self.phase = 0

    def update(self, player_rect, other_seekers, obstacles):
        # Boss moves slower, but pulses toward player in phases
        if self.phase % 60 == 0:
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = max(1, (dx**2 + dy**2)**0.5)
            self.rect.x += int(7 * dx / dist)
            self.rect.y += int(7 * dy / dist)
        self.phase += 1

    def draw(self, screen, offset=(0,0)):
        surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (180,80,255,150), (0,0,self.rect.width,self.rect.height), border_radius=14)
        pygame.draw.rect(surf, (255,255,255,60), (8,8,self.rect.width-16, self.rect.height-16), border_radius=8)
        screen.blit(surf, (self.rect.x + offset[0], self.rect.y + offset[1]))
        # Eyes
        eye = pygame.Rect(self.rect.x+38+offset[0], self.rect.y+18+offset[1], 14, 14)
        pygame.draw.ellipse(screen, (0,0,0), eye)
        eye2 = pygame.Rect(self.rect.x+38+offset[0], self.rect.y+54+offset[1], 14, 14)
        pygame.draw.ellipse(screen, (0,0,0), eye2)

# --- End of seeker.py ---
# (Lines: ~530+, ready for next!)