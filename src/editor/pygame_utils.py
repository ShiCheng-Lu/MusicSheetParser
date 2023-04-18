import pygame
from common.label import Bbox

def to_pygame_rect(bbox: Bbox):
    return pygame.Rect(bbox.x_min, bbox.y_min, bbox.width, bbox.height)

