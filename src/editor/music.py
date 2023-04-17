import common.music

import pygame

pygame.font.init()
font = pygame.font.Font('freesansbold.ttf', 20)
REST_LABELS = [
    "restDoubleWhole",
    "restWhole",
    "restHalf",
    "restQuarter",
    "rest8th",
    "rest16th",
    "rest32nd",
    "rest64th",
    "rest128th",
]
rest_text = font.render("rest", True, (25, 25, 255))
PITCH_MAP_LABEL = {
    pitch : font.render(pitch, True, (25, 25, 255))
    for pitch in common.music.TONE_MAP
} | {
    rest : rest_text
    for rest in REST_LABELS
}

class Note(common.music.Note):
    def __init__(self, note: common.music.Note):
        note.copy(self)
        self.text = PITCH_MAP_LABEL[self.name]


