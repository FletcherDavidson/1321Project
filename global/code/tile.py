import pygame
from constants import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, spriteType, surface=pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)
        self.spriteType = spriteType
        self.image = surface
        if spriteType == 'object':
            self.rect = self.image.get_rect(
                topleft=(pos[0], pos[1] - TILESIZE))  # Moves larger objects further up to prevent overlapping elements
        else:
            self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -10)  # Keeps x the same shrinks y by 20(top and bottom)
        self.mask = pygame.mask.from_surface(self.image)
