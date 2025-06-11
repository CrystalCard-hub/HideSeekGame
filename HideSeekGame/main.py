# main.py

import pygame
import sys
import random
import time

from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SEEKER_SPAWN_INTERVAL, SEEKER_SPEED_EASY, SEEKER_SPEED_HARD, FONT_NAME
from menu import Menu
from player import Player
from seeker import Seeker
from settings import GameSettings

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hide and Seek")
clock = pygame.time.Clock()

def game_loop():
    game_settings = GameSettings()
    menu = Menu(screen)
    game_state = "menu"

    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, game_settings.theme['player'])
    seekers = []
    spawn_timer = time.time()
    score_timer = time.time()
    score = 0

    while True:
        if game_state == "menu":
            menu.settings = game_settings
            menu.draw()
            result = menu.handle_input()
            if result == "play":
                game_settings = menu.settings
                player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, game_settings.theme['player'])
                seekers = []
                spawn_timer = time.time()
                score_timer = time.time()
                score = 0
                game_state = "playing"
            elif result == "settings":
                menu.show_settings()
            elif result == "exit":
                pygame.quit()
                sys.exit()

        elif game_state == "playing":
            screen.fill(game_settings.theme['bg'])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            player.update()

            # Seeker spawn
            if time.time() - spawn_timer >= SEEKER_SPAWN_INTERVAL / FPS:
                color = game_settings.theme['seeker_easy'] if game_settings.difficulty == "Easy" else game_settings.theme['seeker_hard']
                speed = SEEKER_SPEED_EASY if game_settings.difficulty == "Easy" else SEEKER_SPEED_HARD
                seekers.append(Seeker(random.randint(0, SCREEN_WIDTH - 40), random.randint(0, SCREEN_HEIGHT - 40), speed, color))
                spawn_timer = time.time()

            # Score increase
            if time.time() - score_timer >= 1:
                score += 143
                score_timer = time.time()

            for seeker in seekers:
                seeker.update(player.rect.center)
                seeker.draw(screen)
                if seeker.rect.colliderect(player.rect):
                    game_state = "menu"  # restart game
                    break

            player.draw(screen)

            font = pygame.font.Font(FONT_NAME, 24)
            spawn_time_left = max(0, int(SEEKER_SPAWN_INTERVAL / FPS - (time.time() - spawn_timer)))
            text1 = font.render(f"Next Seeker: {spawn_time_left}s", True, (255, 255, 255))
            text2 = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(text1, (10, 10))
            screen.blit(text2, (10, 40))

            pygame.display.update()
            clock.tick(FPS)

if __name__ == "__main__":
    game_loop()