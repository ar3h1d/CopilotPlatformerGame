# File: src/main.py
import pygame
import sys
import os

from player import Player
from level_generator import LevelGenerator
from collectible import Collectible

# Screen (window) dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Level (world) dimensions
LEVEL_WIDTH = 1600
LEVEL_HEIGHT = 1200

# Ground level (y-coordinate for ground platform)
GROUND_Y = LEVEL_HEIGHT - 50

# Define a pause button rectangle (positioned in the top right corner)
PAUSE_BUTTON_RECT = pygame.Rect(SCREEN_WIDTH - 110, 10, 100, 40)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Camera Class ---
class Camera:
    def __init__(self, level_width, level_height):
        self.camera_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.level_width = level_width
        self.level_height = level_height

    def apply(self, target_rect):
        """Return a rect shifted by the camera's offset."""
        return target_rect.move(-self.camera_rect.x, -self.camera_rect.y)

    def update(self, target):
        """Center the camera on target (usually the player) and clamp within level bounds."""
        x = target.rect.centerx - SCREEN_WIDTH // 2
        y = target.rect.centery - SCREEN_HEIGHT // 2
        x = max(0, min(x, self.level_width - SCREEN_WIDTH))
        y = max(0, min(y, self.level_height - SCREEN_HEIGHT))
        self.camera_rect = pygame.Rect(x, y, SCREEN_WIDTH, SCREEN_HEIGHT)

# --- Main Menu ---
def main_menu(screen, clock, font, large_font):
    while True:
        screen.fill((0, 0, 50))
        title_text = large_font.render("Copilot Platformer Game", True, (255, 255, 0))
        instr_text = font.render("Press ENTER to Start, ESC to Quit", True, (255, 255, 255))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2,
                                 SCREEN_HEIGHT // 2 - 100))
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2,
                                 SCREEN_HEIGHT // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return 'start'
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
        clock.tick(60)

# --- Pause Menu ---
def pause_menu(screen, clock, font, large_font):
    while True:
        screen.fill((30, 30, 30))
        pause_text = large_font.render("Paused", True, (255, 255, 255))
        instr_text = font.render("Press P to Resume  |  R to Restart  |  M for Main Menu", True, (255, 255, 255))
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                  SCREEN_HEIGHT // 2 - 100))
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2,
                                  SCREEN_HEIGHT // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    return 'resume'
                elif event.key == pygame.K_r:
                    return 'restart'
                elif event.key == pygame.K_m:
                    return 'menu'
        clock.tick(60)

# --- Game Over Menu (also used for Win) ---
def game_over_menu(screen, clock, font, large_font, win):
    while True:
        screen.fill((0, 0, 0))
        if win:
            result_text = large_font.render("You Win!", True, (0, 255, 0))
        else:
            result_text = large_font.render("Game Over", True, (255, 0, 0))
        instr_text = font.render("Press R to Restart or M for Main Menu", True, (255, 255, 255))
        screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2,
                                  SCREEN_HEIGHT // 2 - 100))
        screen.blit(instr_text, (SCREEN_WIDTH // 2 - instr_text.get_width() // 2,
                                 SCREEN_HEIGHT // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return 'restart'
                elif event.key == pygame.K_m:
                    return 'menu'
        clock.tick(60)

# --- Main Game Loop (run_game) ---
def run_game(screen, clock, font, large_font):
    # Set spawn near the ground.
    player_spawn_y = GROUND_Y - 80
    player = Player(100, player_spawn_y)
    player.health = 5
    player.invulnerable = False
    player.invulnerable_timer = 0

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    level_gen = LevelGenerator(LEVEL_WIDTH, LEVEL_HEIGHT, GROUND_Y, num_platforms=10, enemy_chance=0.6)
    platform_sprites, enemy_sprites = level_gen.generate_level()
    all_sprites.add(platform_sprites)
    all_sprites.add(enemy_sprites)

    collectible_sprites = pygame.sprite.Group()
    for platform in platform_sprites:
        if platform.rect.top < GROUND_Y:
            col = Collectible(platform.rect.centerx, platform.rect.top - 10)
            collectible_sprites.add(col)
    all_sprites.add(collectible_sprites)
    total_collectibles = len(collectible_sprites)

    camera = Camera(LEVEL_WIDTH, LEVEL_HEIGHT)
    win = False
    game_over = False

    while not game_over:
        # Process events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            # Pause key handling.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause_choice = pause_menu(screen, clock, font, large_font)
                    if pause_choice in ['restart', 'menu']:
                        return pause_choice
            # Also check for mouse clicks on the pause button.
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if PAUSE_BUTTON_RECT.collidepoint(pos):
                    pause_choice = pause_menu(screen, clock, font, large_font)
                    if pause_choice in ['restart', 'menu']:
                        return pause_choice

            # Regular controls.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                elif event.key == pygame.K_RIGHT:
                    player.go_right()
                elif event.key == pygame.K_SPACE:
                    player.jump()
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    player.stop()

        # Update sprites.
        player.update()
        enemy_sprites.update()

        # Platform collision.
        if player.change_y >= 0:
            collisions = pygame.sprite.spritecollide(player, platform_sprites, False)
            for platform in collisions:
                if player.rect.bottom >= platform.rect.top and \
                   player.rect.bottom - player.change_y <= platform.rect.top:
                    player.rect.bottom = platform.rect.top
                    player.change_y = 0
                    player.on_ground = True
                    break
            else:
                player.on_ground = False
        else:
            player.on_ground = False

        # Enemy collision using the custom hitbox callback.
        if pygame.sprite.spritecollide(player, enemy_sprites, False,
                                       collided=lambda p, e: p.rect.colliderect(e.hitbox)):
            if not player.invulnerable:
                player.health -= 1
                player.set_animation("hurt")
                player.invulnerable = True
                player.invulnerable_timer = pygame.time.get_ticks()
        if player.invulnerable and pygame.time.get_ticks() - player.invulnerable_timer > 2000:
            player.invulnerable = False

        if player.health <= 0:
            game_over = True

        # Collectible collisions.
        collected = pygame.sprite.spritecollide(player, collectible_sprites, True)
        if collected:
            print(f"Collected {len(collected)} item(s)!")
        if len(collectible_sprites) == 0 and total_collectibles > 0:
            win = True
            game_over = True

        camera.update(player)

        # Render scene.
        screen.fill((100, 150, 200))
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite.rect))

        # Draw HUD with health and collectible count.
        hud_text = font.render(f"HP: {player.health}    Collectibles: {total_collectibles - len(collectible_sprites)}/{total_collectibles}", True, (255, 255, 255))
        screen.blit(hud_text, (10, 10))

        # Draw the pause button on screen.
        pygame.draw.rect(screen, (50, 50, 50), PAUSE_BUTTON_RECT)
        pause_label = font.render("Pause (P)", True, (255, 255, 255))
        screen.blit(pause_label, (PAUSE_BUTTON_RECT.centerx - pause_label.get_width() // 2,
                                  PAUSE_BUTTON_RECT.centery - pause_label.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)

    return game_over_menu(screen, clock, font, large_font, win)

# --- Main Function (State Machine) ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Copilot Platformer Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)

    state = main_menu(screen, clock, font, large_font)
    while True:
        if state == 'start':
            result = run_game(screen, clock, font, large_font)
            state = result
        elif state == 'restart':
            state = run_game(screen, clock, font, large_font)
        elif state == 'menu':
            state = main_menu(screen, clock, font, large_font)
        else:
            break

if __name__ == "__main__":
    main()
