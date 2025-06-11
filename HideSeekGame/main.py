import pygame
import time
from player import Player
from seeker import Seeker
from menu import Menu
from config import WIDTH, HEIGHT, WHITE, BLACK, FPS

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

while True:
    screen.fill(WHITE)
    
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

        if player.rect.colliderect(seeker.rect):
            print("You got caught! Restarting...")
            player.rect.topleft = (100, 300)
            seeker.rect.topleft = (500, 300)
            start_time = time.time()
            game_active = False  # Go back to menu

        # Track High Score
        current_score = int(time.time() - start_time)
        if current_score > HIGH_SCORE:
            HIGH_SCORE = current_score

        # Draw game elements
        player.draw(screen)
        seeker.draw(screen)

        score_text = font.render(f"Time Survived: {current_score}s", True, BLACK)
        high_score_text = font.render(f"High Score: {HIGH_SCORE}s", True, BLACK)
        screen.blit(score_text, (20, 20))
        screen.blit(high_score_text, (20, 60))

    pygame.display.flip()
    clock.tick(FPS)
