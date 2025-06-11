import pygame
from player import Player
from seeker import Seeker

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hide and Seek")

# Create player and seeker objects
player = Player(100, 300)
seeker = Seeker(500, 300)

# Game loop
running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get key inputs & move player
    keys = pygame.key.get_pressed()
    player.move(keys)

    # Move seeker randomly
    seeker.move_random()
    
    # Check for collision
if player.rect.colliderect(seeker.rect):
    print("You got caught! Restarting game...")
    player.rect.topleft = (100, 300)  # Reset player position
    seeker.rect.topleft = (500, 300)  # Reset seeker position

    # Draw characters on the screen
    player.draw(screen)
    seeker.draw(screen)

    pygame.display.flip()

pygame.quit()
