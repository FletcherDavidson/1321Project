import pygame
from csv import reader
from os import walk

pygame.init()
font = pygame.font.Font(None, 30)


def debug(info, y=10, x=10):
    display_surface = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, 'White')
    debug_rect = debug_surf.get_rect(topleft=(x, y))
    pygame.draw.rect(display_surface, 'Black', debug_rect)
    display_surface.blit(debug_surf, debug_rect)


def debugDrawMask(self, surface, mask, pos):
    mask_surface = mask.to_surface()
    mask_surface.set_colorkey((0, 0, 0))
    surface.blit(mask_surface, pos)


def importCSVLayout(path):
    terrainMap = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrainMap.append(list(row))
        return terrainMap