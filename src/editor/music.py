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

    def render(self, screen, x, y, scale):
        thickness = 3

        self.renderBox.bbox = [
            self.x_min * scale + x,
            self.y_min * scale + y,
            self.x_max * scale + x,
            self.y_max * scale + y,
        ]

        text = PITCH_MAP_LABEL[self.pitch_str]
        textRect = text.get_rect()
        textRect.x = self.renderBox.x_min
        textRect.bottom = self.renderBox.y_min

        rect = to_pygame_rect(self.renderBox)
        rect.width += thickness
        rect.height += thickness

        pygame.draw.rect(screen, (25, 200, 25), rect, thickness)
        screen.blit(text, textRect)

    def update(self, duration, pitch, modifier):
        self.duration: float = duration
        self.pitch: int = pitch
        self.modifier = modifier

        self.parent_bar.validate()
        pass

class Bar(common.music.Bar):
    def __init__(self, bar: common.music.Bar):
        bar.copy(self)
        self.notes: list[Note] = [Note(note) for note in self.notes]

    def validate(self):
        pass

    def render(self, screen, x, y, scale):
        for note in self.notes:
            note.render(screen, x, y, scale)

class Staff(common.music.Staff):
    def __init__(self, staff: common.music.Staff):
        staff.copy(self)
        self.bars: list[Bar] = [Bar(bar) for bar in self.bars]

    def render(self, screen, x, y, scale):
        for bar in self.bars:
            bar.render(screen, x, y, scale)

class Music(common.music.Music):
    def __init__(self, music: common.music.Music):
        music.copy(self)
        self.staffs: list[Staff] = [Staff(staff) for staff in self.staffs]

    def render(self, screen, x, y, scale):
        for staff in self.staffs:
            staff.render(screen, x, y, scale)
    
    @property
    def notes(self):
        notes = []
        for staff in self.staffs:
            for bar in staff.bars:
                notes.extend(bar.notes)
        return notes
        