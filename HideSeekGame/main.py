# main.py

import pygame
import sys
from config import WIDTH, HEIGHT, FPS, FONT_NAME
from settings import Settings
from player import Player
from seeker import Seeker
from menu import Button, draw_menu, draw_settings, draw_pause, draw_game_over

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hide & Seek")
clock = pygame.time.Clock()
font = pygame.font.Font(FONT_NAME, 28)

settings = Settings()

def game_loop():
    theme = settings.get_theme()
    player = Player(WIDTH//2, HEIGHT//2, theme["player"])
    seekers = []
    seeker_timer = 0
    score = 0
    score_timer = 0
    paused = False

    while True:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True
                if event.key == pygame.K_b:
                    player.try_boost()

        if paused:
            draw_pause(screen)
            while paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_c:
                            paused = False
                        elif event.key == pygame.K_q:
                            return
                clock.tick(FPS)
            continue

        player.update(keys)
        for seeker in seekers:
            seeker.update(player.rect)

        seeker_timer += 1
        score_timer += 1

        if seeker_timer >= FPS * 30:
            color = theme["seeker"] if settings.difficulty == "Easy" else theme["seeker_hard"]
            speed = 2 if settings.difficulty == "Easy" else 4
            seekers.append(Seeker(0, 0, color, speed))
            seeker_timer = 0

        if score_timer >= FPS:
            score += 143
            score_timer = 0

        for seeker in seekers:
            if seeker.rect.colliderect(player.rect):
                settings.high_score = max(settings.high_score, score)
                draw_game_over(screen, score)
                pygame.time.delay(5000)
                return

        screen.fill(theme["bg"])
        player.draw(screen)
        for seeker in seekers:
            seeker.draw(screen)

        timer_text = font.render(f"Seeker Spawn: {30 - seeker_timer // FPS}", True, (255, 255, 255))
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(timer_text, (10, 10))
        screen.blit(score_text, (10, 40))

        pygame.display.flip()
        clock.tick(FPS)

def main():
    play_btn = Button((540, 300, 200, 60), "Play")
    settings_btn = Button((540, 400, 200, 60), "Settings")
    exit_btn = Button((540, 500, 200, 60), "Exit")
    state = "menu"

    while True:
        if state == "menu":
            draw_menu(screen, [play_btn, settings_btn, exit_btn])
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if play_btn.is_clicked(pos):
                        game_loop()
                    elif settings_btn.is_clicked(pos):
                        state = "settings"
                    elif exit_btn.is_clicked(pos):
                        pygame.quit(); sys.exit()
        elif state == "settings":
            draw_settings(screen, settings)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        settings.next_theme()
                    elif event.key == pygame.K_d:
                        settings.toggle_difficulty()
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"

        clock.tick(FPS)

if __name__ == "__main__":
    main()