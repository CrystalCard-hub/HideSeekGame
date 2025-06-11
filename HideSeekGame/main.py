import pygame
import time
from player import Player
from seeker import Seeker

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hide and Seek")

# Initialize game variables
start_time = time.time()
HIGH_SCORE = 0

# Create player and seeker objects
player = Player(100, 300)
seeker = Seeker(500, 300)

# Game loop
running = True
while running:
    screen.fill((255, 255, 255))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get key inputs & move player smoothly
    keys = pygame.key.get_pressed()
    player.move(keys)

    # Move seeker randomly
    seeker.move_random()

    # Check for collision (Game Restart)
    if player.rect.colliderect(seeker.rect):
        print("You got caught! Restarting game...")
        player.rect.topleft = (100, 300)  # Reset player position
        seeker.rect.topleft = (500, 300)  # Reset seeker position
        start_time = time.time()  # Reset timer

    # Track High Score (Time Survived)
    current_score = int(time.time() - start_time)
    if current_score > HIGH_SCORE:
        HIGH_SCORE = current_score
        print(f"New High Score: {HIGH_SCORE}")

    # Draw characters on screen
    player.draw(screen)
    seeker.draw(screen)

    pygame.display.flip()

pygame.quit()
