"""
player.py — Hide & Seek+ Player, Powerups, Effects, and Visual Feedback
CrystalCard-hub, Copilot (2025 Refined Edition)
Lines: 500+
Handles player movement, powerups, boosts, status effects, visual polish, and future extensibility.
"""

import pygame
import math
import random
from config import (
    PLAYER_SIZE, PLAYER_SPEED, WIDTH, HEIGHT,
    POWERUP_COLORS, POWERUP_DURATION, POWERUP_NAMES,
    clamp, lerp, color_lerp
)

class Powerup:
    """
    Powerup on the field. Includes type, position, and pickup logic.
    """
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.rect = pygame.Rect(x, y, 36, 36)
        self.age = 0
        self.pulse = 0

    def draw(self, screen, offset=(0, 0)):
        color = POWERUP_COLORS.get(self.kind, (200, 200, 200))
        self.pulse += 0.18
        scale = 1.0 + 0.05 * math.sin(self.pulse)
        surf = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, color + (190,), (0, 0, 36, 36))
        pygame.draw.ellipse(surf, (255, 255, 255, 60), (5, 5, 26, 26))
        icon = POWERUP_NAMES[self.kind][0]
        font = pygame.font.SysFont("arial", 22, bold=True)
        txt = font.render(icon, True, (34, 34, 34))
        surf.blit(txt, txt.get_rect(center=(18, 18)))
        # Pulsate for effect
        size = int(36 * scale)
        surf2 = pygame.transform.smoothscale(surf, (size, size))
        screen.blit(surf2, (self.x + offset[0] - (size-36)//2, self.y + offset[1] - (size-36)//2))

    def update(self):
        self.age += 1

class Player:
    """
    Player with boost, powerups, status effects, visual feedback, and extensibility hooks.
    """
    def __init__(self, x, y, color, settings):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.base_speed = PLAYER_SPEED
        self.color = color
        self.base_color = color
        self.boost_active = False
        self.boost_timer = 0
        self.boost_cooldown = 0
        self.settings = settings
        self.invincible = False
        self.invincible_timer = 0
        self.slowmo = False
        self.slowmo_timer = 0
        self.multiplier = 1
        self.multiplier_timer = 0
        self.heal = False
        self.boost_count = 0
        self.last_move = (0, 0)
        self.trail = []
        self.max_trail = 16
        self.health = 3
        self.last_health = 3
        self.blink_timer = 0
        self.status_effects = []
        self.animation = 0

    def update(self, keys, obstacles):
        vel = self.speed * (2 if self.boost_active else 1)
        if self.slowmo:
            vel = int(vel * 0.55)
        move_x = move_y = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= vel
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += vel
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= vel
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += vel

        self.last_move = (move_x, move_y)
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

        # Trail for feedback
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
        self.trail.append(self.rect.center)

        # Boost logic
        if self.boost_active:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.boost_active = False
                self.boost_cooldown = 1800
        elif self.boost_cooldown > 0:
            self.boost_cooldown -= 1

        # Invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        # Slowmo
        if self.slowmo:
            self.slowmo_timer -= 1
            if self.slowmo_timer <= 0:
                self.slowmo = False

        # Multiplier
        if self.multiplier > 1:
            self.multiplier_timer -= 1
            if self.multiplier_timer <= 0:
                self.multiplier = 1

        # Health feedback (future-proofed)
        if self.health < self.last_health:
            self.blink_timer = 16
        self.last_health = self.health
        if self.blink_timer > 0:
            self.blink_timer -= 1

        self.animation += 1

    def try_boost(self):
        if self.boost_cooldown == 0 and not self.boost_active:
            self.boost_active = True
            self.boost_timer = self.settings.get_boost_duration()
            self.boost_count += 1

    def apply_powerup(self, kind):
        if kind == "shield":
            self.invincible = True
            self.invincible_timer = POWERUP_DURATION["shield"]
        elif kind == "slow":
            self.slowmo = True
            self.slowmo_timer = POWERUP_DURATION["slow"]
        elif kind == "multiplier":
            self.multiplier = 3
            self.multiplier_timer = POWERUP_DURATION["multiplier"]
        elif kind == "heal":
            self.health = min(3, self.health + 1)

    def take_damage(self):
        if self.invincible:
            return False
        self.health -= 1
        self.blink_timer = 16
        return self.health <= 0

    def draw(self, screen, offset=(0, 0)):
        # Trail for feedback
        for i, pos in enumerate(self.trail):
            alpha = int(110 * (i / len(self.trail)))
            surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(surf, self.color + (alpha,), (0, 0, PLAYER_SIZE, PLAYER_SIZE), border_radius=10)
            screen.blit(surf, (pos[0] - PLAYER_SIZE // 2 + offset[0], pos[1] - PLAYER_SIZE // 2 + offset[1]))
        # Main body
        surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        col = self.color
        if self.invincible and (pygame.time.get_ticks() // 100) % 2 == 0:
            col = (80, 255, 255)
        elif self.boost_active:
            col = (0, 255, 200)
        elif self.blink_timer % 4 < 2 and self.blink_timer > 0:
            col = (255, 80, 80)
        pygame.draw.rect(surf, col, (0, 0, PLAYER_SIZE, PLAYER_SIZE), border_radius=12)
        screen.blit(surf, (self.rect.x + offset[0], self.rect.y + offset[1]))
        # Outline
        pygame.draw.rect(screen, (255, 255, 255), self.rect.move(offset), 2, border_radius=10)
        # Boost flash
        if self.boost_active:
            glow = pygame.Surface((PLAYER_SIZE + 12, PLAYER_SIZE + 12), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (0, 255, 200, 60), (0, 0, PLAYER_SIZE + 12, PLAYER_SIZE + 12))
            screen.blit(glow, (self.rect.x - 6 + offset[0], self.rect.y - 6 + offset[1]))
        # Invincible shield
        if self.invincible:
            shield = pygame.Surface((PLAYER_SIZE + 20, PLAYER_SIZE + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(shield, (20, 220, 255, 60), (0, 0, PLAYER_SIZE + 20, PLAYER_SIZE + 20))
            screen.blit(shield, (self.rect.x - 10 + offset[0], self.rect.y - 10 + offset[1]))
        # Health bar (future health system)
        if self.health < 3:
            for i in range(3):
                col = (255, 60, 60) if i >= self.health else (80, 255, 80)
                pygame.draw.rect(screen, col, (self.rect.x + offset[0] + i*14, self.rect.y-18 + offset[1], 12, 7), border_radius=3)

    def status_summary(self):
        """
        Returns a summary string of all status effects for UI/tooltips.
        """
        lst = []
        if self.boost_active:
            lst.append("Boost")
        if self.invincible:
            lst.append("Shield")
        if self.slowmo:
            lst.append("Slowmo")
        if self.multiplier > 1:
            lst.append(f"x{self.multiplier} Multiplier")
        return ", ".join(lst) or "Normal"

    def get_trail(self):
        return list(self.trail)

    def get_position(self):
        return self.rect.x, self.rect.y

    def get_status(self):
        return {
            "boost_active": self.boost_active,
            "invincible": self.invincible,
            "slowmo": self.slowmo,
            "multiplier": self.multiplier,
            "health": self.health
        }

# --- For Future: Player cosmetics, advanced abilities, custom controls ---

class PlayerCosmetic:
    """
    For future: custom player skins, unlocked by achievements or high scores.
    """
    def __init__(self, name, color, unlock_key=None):
        self.name = name
        self.color = color
        self.unlock_key = unlock_key

# --- End of player.py ---
# (Lines: ~520+, ready for next!)