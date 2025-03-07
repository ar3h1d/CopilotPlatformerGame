# File: src/player.py
import pygame
import os
import sys

def resource_path(relative_path):
    """
    Get absolute path to resource, works for development and for PyInstaller.
    When frozen by PyInstaller, resources are unpacked into sys._MEIPASS.
    """
    try:
        # PyInstaller stores data files in sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Define the animations to support, with their corresponding frame counts.
        self.animation_specs = {
            "idle": 4,
            "death": 6,
            "doublejump": 6,
            "hurt": 2,
            "jump": 4,
            "run": 6,
        }

        self.animations = {}
        self.scale = (80, 80)  # Set a larger character size.
        # Loop through each animation type and load its frames.
        for anim, frame_count in self.animation_specs.items():
            # Build the path using resource_path to include bundled assets.
            path = resource_path(os.path.join("assets", "player", f"{anim}.png"))
            frames = self.load_animation(path, frame_count, self.scale)
            self.animations[anim] = frames
            # Precompute the left-facing frames to avoid runtime flipping issues.
            self.animations[anim + "_left"] = [pygame.transform.flip(frame, True, False) for frame in frames]

        self.current_animation = "idle"
        self.current_frame = 0
        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Animation timing in seconds per frame.
        self.animation_speed = 0.1
        self.last_update_time = pygame.time.get_ticks()

        # Movement and physics attributes.
        self.change_x = 0
        self.change_y = 0
        self.on_ground = False

        # 1 indicates the sprite is facing right, -1 means left.
        self.facing = 1

    def load_animation(self, path, frame_count, scale):
        """
        Loads a sprite sheet from the given path and slices it into frame_count frames.
        Each frame is then scaled to the desired size.
        """
        frames = []
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error loading animation from {path}: {e}")
            fallback = pygame.Surface(scale)
            fallback.fill((255, 0, 0))
            return [fallback]

        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // frame_count
        for i in range(frame_count):
            frame_rect = (i * frame_width, 0, frame_width, sheet_height)
            frame = sheet.subsurface(frame_rect)
            # Scale the frame to the desired size.
            frame = pygame.transform.scale(frame, scale)
            frames.append(frame)
        return frames

    def set_animation(self, animation):
        """
        If the desired animation is different from the current one,
        switch to it and reset the frame counter.
        """
        if animation != self.current_animation and animation in self.animations:
            self.current_animation = animation
            self.current_frame = 0
            self.last_update_time = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.animation_speed * 1000:
            self.last_update_time = now
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.current_animation])

        # Use the precomputed flipped frames based on the facing direction.
        if self.facing == -1:
            current_anim = self.current_animation + "_left"
        else:
            current_anim = self.current_animation
        self.image = self.animations[current_anim][self.current_frame]

        # Apply gravity and update position.
        self.change_y += 1
        self.rect.x += self.change_x
        self.rect.y += self.change_y

    def jump(self):
        if self.on_ground:
            self.change_y = -20  # Jump strength.
            self.on_ground = False
            self.set_animation("jump")

    def go_left(self):
        self.change_x = -5
        self.facing = -1  # Facing left.
        self.set_animation("run")

    def go_right(self):
        self.change_x = 5
        self.facing = 1  # Facing right.
        self.set_animation("run")

    def stop(self):
        self.change_x = 0
        self.set_animation("idle")
