# File: src/platform.py
import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=(0, 255, 0)):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
