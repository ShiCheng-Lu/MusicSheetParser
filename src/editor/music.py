import common.music
from common.label import Bbox

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

    def render(self, screen, x, y, scale):
        thickness = 3

        render_x = self.x_min * scale + x
        render_y = self.y_min * scale + y
        render_w = self.width * scale + thickness
        render_h = self.height * scale + thickness

        text = PITCH_MAP_LABEL[self.pitch_str]
        textRect = text.get_rect()
        textRect.x = render_x
        textRect.bottom = render_y

        pygame.draw.rect(screen, (25, 200, 25), [render_x, render_y, render_w, render_h], thickness)
        screen.blit(text, textRect)

    def update(self):
        pass

# class Bar(common.music.Bar):
#     def 