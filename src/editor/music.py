import common.music
from common.label import Bbox
from editor.bar_editor import Bar
from editor.note_editor import Note

import pygame

pygame.font.init()
font = pygame.font.Font('freesansbold.ttf', 20)

PITCH_MAP_LABEL = {
    pitch : font.render(pitch, True, (25, 25, 255))
    for pitch in common.music.SEMITONE_MAP
} | {
    'rest': font.render("rest", True, (25, 25, 255))
}

class Staff(common.music.Staff):
    def __init__(self, staff: common.music.Staff, parent_music):
        staff.copy(self)
        self.parent_music = parent_music
        self.bars: list[Bar] = [Bar(bar, self) for bar in self.bars]

    def render(self, screen):
        for bar in self.bars:
            bar.render(screen)

class Music(common.music.Music):
    def __init__(self, music: common.music.Music):
        music.copy(self)
        self.staffs: list[Staff] = [Staff(staff, self) for staff in self.staffs]

    def render(self, screen):
        for staff in self.staffs:
            staff.render(screen)
    
    @property
    def notes(self):
        notes = []
        for staff in self.staffs:
            for bar in staff.bars:
                notes.extend(bar.notes)
        return notes
