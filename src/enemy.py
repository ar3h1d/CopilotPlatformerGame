# File: src/enemy.py
import pygame
import os
import sys

def resource_path(relative_path):
    """
    Get the absolute path to a resource, works for development and PyInstaller packed executables.
    When frozen by PyInstaller, resources are unpacked into sys._MEIPASS.
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller temporary folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_distance=100, speed=2):
        super().__init__()

        # Define the animations to support (here we assume an enemy walk cycle).
        # For example, if your enemy walk cycle has 4 frames:
        self.animation_specs = {"walk": 4}
        self.animations = {}
        self.scale = (40, 40)  # Enemy sprite size

        # Load each animation using resource_path
        for anim, frame_count in self.animation_specs.items():
            path = resource_path(os.path.join("assets", "enemy", f"{anim}.png"))
            frames = self.load_animation(path, frame_count, self.scale)
            self.animations[anim] = frames
            # Precompute left-facing frames.
            self.animations[anim + "_left"] = [pygame.transform.flip(frame, True, False) for frame in frames]

        self.current_animation = "walk"
        self.current_frame = 0
        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Create a separate, smaller hitbox (for better collision detection)
        hitbox = self.rect.inflate(-20, -20)
        hitbox.center = self.rect.center
        self.hitbox = hitbox

        self.animation_speed = 0.15  # Seconds per frame
        self.last_update_time = pygame.time.get_ticks()

        # Movement attributes for patrolling.
        self.starting_x = x
        self.patrol_distance = patrol_distance
        self.speed = speed
        self.direction = 1  # 1 for moving right, -1 for left.
        self.facing = 1     # 1 for facing right, -1 for facing left.

    def load_animation(self, path, frame_count, scale):
        """
        Loads a sprite sheet from the given path and splits it into frame_count frames.
        Each frame is scaled to the provided dimensions.
        """
        frames = []
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error loading enemy animation from {path}: {e}")
            fallback = pygame.Surface(scale)
            fallback.fill((0, 0, 255))
            return [fallback]

        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // frame_count
        for i in range(frame_count):
            frame_rect = (i * frame_width, 0, frame_width, sheet_height)
            frame = sheet.subsurface(frame_rect)
            frame = pygame.transform.scale(frame, scale)
            frames.append(frame)
        return frames

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.animation_speed * 1000:
            self.last_update_time = now
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])

        # Choose the appropriate animation set based on facing direction.
        if self.facing == -1:
            current_anim = self.current_animation + "_left"
        else:
            current_anim = self.current_animation
        self.image = self.animations[current_anim][self.current_frame]

        # Update movement (patrol)
        self.rect.x += self.speed * self.direction
        self.hitbox.x += self.speed * self.direction

        # Reverse direction if exceeding patrol boundaries.
        if self.rect.x > self.starting_x + self.patrol_distance:
            self.direction = -1
            self.facing = -1
        elif self.rect.x < self.starting_x - self.patrol_distance:
            self.direction = 1
            self.facing = 1
