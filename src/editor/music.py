import common.music
from common.label import Bbox
from editor.pygame_utils import to_pygame_rect

import pygame

pygame.font.init()
font = pygame.font.Font('freesansbold.ttf', 20)

PITCH_MAP_LABEL = {
    pitch : font.render(pitch, True, (25, 25, 255))
    for pitch in common.music.TONE_MAP
} | {
    'rest': font.render("rest", True, (25, 25, 255))
}

class Note(common.music.Note):
    def __init__(self, note: common.music.Note):
        note.copy(self)
        self.renderBox = Bbox()

    def render(self, screen):
        thickness = 3

        text = PITCH_MAP_LABEL[self.pitch_str]
        textRect = text.get_rect()
        textRect.x = self.renderBox.x_min
        textRect.bottom = self.renderBox.y_min

        rect = to_pygame_rect(self.renderBox)
        rect.width += thickness
        rect.height += thickness

        pygame.draw.rect(screen, (25, 200, 25), rect, thickness)
        screen.blit(text, textRect)

    def update(self, x, y, scale):
        self.renderBox.bbox = [
            self.x_min * scale + x,
            self.y_min * scale + y,
            self.x_max * scale + x,
            self.y_max * scale + y,
        ]
