# File: src/level_generator.py
import random
import pygame
from platform import Platform
from enemy import Enemy

class LevelGenerator:
    def __init__(self, screen_width, screen_height, ground_y, num_platforms=5, enemy_chance=0.5):
        """
        Parameters:
            screen_width, screen_height: Dimensions of the level (world).
            ground_y: The y-coordinate where the ground platform sits.
            num_platforms: Total number of floating platforms to generate.
            enemy_chance: Probability (0 to 1) of spawning an enemy on a given platform.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ground_y = ground_y
        self.num_platforms = num_platforms
        self.enemy_chance = enemy_chance

    def generate_level(self):
        """
        Generates a random level layout with a reachable "main chain" of platforms:

          1. Ground platform: covers the bottom of the level.
          2. Main chain: Generates 60% of the platforms sequentially with vertical gaps of 30 to 80 pixels.
          3. Extra platforms: Attempts to generate the remainder, but only accepts extra platforms
             if they are within a maximum vertical gap (150 pixels) of any already accessible platform.
          4. Enemies are spawned on platforms (with lower enemy speeds) based on a given chance.

        Returns:
            A tuple of sprite groups: (platform_sprites, enemy_sprites)
        """
        platform_sprites = pygame.sprite.Group()
        enemy_sprites = pygame.sprite.Group()

        # 1. Create the ground platform.
        ground = Platform(0, self.ground_y, self.screen_width, 50, color=(0, 255, 0))
        platform_sprites.add(ground)

        # This list will keep track of platforms that are known to be reachable.
        accessible_platforms = []

        # 2. Generate a main chain (60% of total platforms).
        chain_count = max(1, int(self.num_platforms * 0.6))
        # Start a little above the ground.
        current_y = self.ground_y - 60

        for _ in range(chain_count):
            # Increase platform size by using a larger width range.
            width = random.randint(120, 250)
            height = random.randint(20, 30)
            x = random.randint(0, self.screen_width - width)

            # Use a low vertical gap for easier jumps (30 to 80 pixels).
            gap = random.randint(30, 80)
            current_y = max(50, current_y - gap)

            plat = Platform(x, current_y, width, height, color=(0, 200, 0))
            accessible_platforms.append(plat)
            platform_sprites.add(plat)

            # With a certain probability, spawn an enemy on this platform.
            if random.random() < self.enemy_chance:
                enemy_x = x + random.randint(0, max(0, width - 40))
                enemy_y = current_y - 40  # Positioned just above the platform.
                enemy_speed = random.choice([1, 2])  # Slower enemy speeds.
                enemy = Enemy(enemy_x, enemy_y, patrol_distance=random.randint(50, 100), speed=enemy_speed)
                enemy_sprites.add(enemy)

        # 3. Generate extra platforms.
        extra_count = self.num_platforms - chain_count
        extra_platforms = []
        max_vertical_gap = 150  # Extra platforms must be within 150 pixels vertically from an accessible platform.
        attempts = 0  # Limit number of attempts to avoid an infinite loop.
        while len(extra_platforms) < extra_count and attempts < extra_count * 10:
            attempts += 1
            width = random.randint(100, 180)
            height = random.randint(15, 25)
            x = random.randint(0, self.screen_width - width)
            # Restrict y to be between the highest main-chain platform and the ground.
            min_chain_y = min(p.rect.top for p in accessible_platforms) if accessible_platforms else 50
            y = random.randint(min_chain_y, self.ground_y - 100)

            # Check if this candidate platform is reachable from any platform in accessible_platforms.
            reachable = False
            for p in accessible_platforms:
                # Consider it reachable if it is above an accessible platform by no more than max_vertical_gap.
                if y < p.rect.top:
                    if (p.rect.top - y) <= max_vertical_gap:
                        reachable = True
                        break
            if reachable:
                plat = Platform(x, y, width, height, color=(0, 180, 0))
                extra_platforms.append(plat)
                accessible_platforms.append(plat)

        # Add extra platforms to the sprite group.
        for plat in extra_platforms:
            platform_sprites.add(plat)
            if random.random() < self.enemy_chance * 0.5:
                enemy_x = plat.rect.left + random.randint(0, max(0, plat.rect.width - 40))
                enemy_y = plat.rect.top - 40
                enemy_speed = random.choice([1, 2])
                enemy = Enemy(enemy_x, enemy_y, patrol_distance=random.randint(50, 100), speed=enemy_speed)
                enemy_sprites.add(enemy)

        return platform_sprites, enemy_sprites
