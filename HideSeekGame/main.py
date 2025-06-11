import pygame
import time
import random
from player import Player
from seeker import Seeker
from menu import Menu
from config import WIDTH, HEIGHT, BACKGROUND_COLOR, WHITE, YELLOW, RED, LIFE_RED, FPS, RED_BOX_SPAWN_TIME, LIFE_DOT_REQUIREMENT

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hide and Seek")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

menu = Menu()
player = Player(100, 300)
seeker = Seeker(500, 300)

start_time = time.time()
HIGH_SCORE = 0
game_active = False
yellow_dots = []  # List of yellow dots
red_boxes = []  # List of red danger boxes
red_dots = []  # Life boost dots
dot_timer = {}  # Tracks time for each yellow dot

# Spawn initial collectibles
for _ in range(5):
    yellow_dots.append(pygame.Rect(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), 20, 20))

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
                elif action == "Exit":
                    pygame.quit()
                    exit()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        player.move(keys)
        seeker.move(player)

        # Handle collectibles
        for dot in yellow_dots:
            pygame.draw.rect(screen, YELLOW, dot)
            if player.rect.colliderect(dot):
                yellow_dots.remove(dot)
                red_dots.append(pygame.Rect(dot.x, dot.y, 10, 10))  # Convert to red dot
            elif time.time() - dot_timer.get((dot.x, dot.y), time.time()) > RED_BOX_SPAWN_TIME:
                yellow_dots.remove(dot)
                red_boxes.append(pygame.Rect(dot.x, dot.y, 30, 30))  # Convert to red box

        for box in red_boxes:
            pygame.draw.rect(screen, RED, box)
            if player.rect.colliderect(box):
                print("Hit red box! Lost a life.")
                player.lives -= 1
                red_boxes.remove(box)

        for red_dot in red_dots:
            pygame.draw.rect(screen, LIFE_RED, red_dot)
            if player.rect.colliderect(red_dot):
                red_dots.remove(red_dot)

        if len(red_dots) >= LIFE_DOT_REQUIREMENT:
            player.lives += 1
            red_dots.clear()  # Reset dots after gaining life

        # Check for losing condition
        if player.lives <= 0:
            print("Game Over! Restarting...")
            player.rect.topleft = (100, 300)
            seeker.rect.topleft = (500, 300)
            start_time = time.time()
            player.lives = 3
            game_active = False

        player.draw(screen)
        seeker.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)
