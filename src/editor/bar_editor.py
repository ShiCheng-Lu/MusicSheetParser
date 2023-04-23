import common.music
import pygame_gui
import pygame
import editor.pygame_utils
from editor.note_editor import Note
from common.label import Bbox

width = 180
menu = None

class BarEditorMenu():
    def __init__(self, manager) -> None:
        global menu
        menu = self

        self.panel = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect(900, 0, 180, 860))

        self.duration_selector = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self.panel,
            manager=manager,)
        self.add_note_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, width, 50),
            container=self.panel,
            manager=manager,
            text="Add Note")


class Bar(common.music.Bar):
    def __init__(self, bar: common.music.Bar, parent_staff):
        bar.copy(self)
        self.parent_staff = parent_staff
        self.notes: list[Note] = [Note(note, self) for note in self.notes]

        self.valid = False
        self.validate()

    def validate(self):
        duration = 0
        target_duration = self.parent_staff.parent_music.time_sig_duration

        group_duration = 0
        group_x_end = 0
        for note in sorted(self.notes, key=lambda x: x.x_min):
            if note.x_min > group_x_end:
                # new group
                duration += group_duration
                group_x_end = note.x_max
                group_duration = note.duration
            else:
                group_duration = max(group_duration, note.duration)
                group_x_end = max(group_x_end, note.x_max)
        duration += group_duration

        self.valid = duration % target_duration == 0

    def render(self, screen):
        for note in self.notes:
            note.render(screen)
        
        # don't outline if its valid
        if self.valid:
            return

        thickness = 3

        rect = editor.pygame_utils.to_pygame_rect(self)
        pygame.draw.rect(screen, (200, 25, 25), rect, thickness)
    
    def delete_note(self, note):
        self.notes.remove(note)
    
    def select(self, pos: Bbox):
        for note in self.notes:
            if result := note.select(pos):
                return result
        if self.intersects(pos):
            return self
