# File: src/collectible.py
import pygame

class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a simple yellow circle for the collectible
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 223, 0), (10, 10), 10)
        self.rect = self.image.get_rect(center=(x, y))
