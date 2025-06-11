import pygame
import time
import random
from player import Player
from seeker import Seeker
from menu import Menu
from settings import Settings
from config import WIDTH, HEIGHT, BACKGROUND_COLOR, WHITE, YELLOW, RED, LIFE_RED, FPS, RED_BOX_SPAWN_TIME, LIFE_DOT_REQUIREMENT

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hide and Seek")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

menu = Menu()
settings = Settings()
player = Player(100, 300)
seeker = Seeker(500, 300)

start_time = time.time()
HIGH_SCORE = 0
game_active = False
yellow_dots = [pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20) for _ in range(5)]
red_boxes = []
red_dots = []
dot_timer = {}

while True:
    screen.fill(BACKGROUND_COLOR)
    
    if not game_active:
        menu.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                action = menu.navigate(event.key)
                if action == "Play":
                    game_active = True
                    start_time = time.time()
                elif action == "Settings":
                    settings.draw(screen)
                elif action == "Exit":
                    pygame.quit()
                    exit()
    else:
        player.move(pygame.key.get_pressed())
        seeker.move(player)

        for dot in yellow_dots:
            pygame.draw.rect(screen, YELLOW, dot)
            if player.rect.colliderect(dot):
                yellow_dots.remove(dot)
                red_dots.append(pygame.Rect(dot.x, dot.y, 10, 10))
            elif time.time() - dot_timer.get((dot.x, dot.y), time.time()) > RED_BOX_SPAWN_TIME:
                yellow_dots.remove(dot)
                red_boxes.append(pygame.Rect(dot.x, dot.y, 30, 30))

        player.draw(screen)
        seeker.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)
